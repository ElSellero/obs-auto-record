"""Kernlogik: Scheduling, OBS-Steuerung, Netflix-Oeffnung."""

import subprocess
import time
from datetime import datetime, timedelta


class Recorder:
    """Steuert den gesamten Aufnahme-Workflow."""

    def __init__(self, status_callback):
        """
        Args:
            status_callback: Funktion(status_text, is_finished) die bei
                             Statusaenderungen aufgerufen wird.
        """
        self.status_callback = status_callback
        self._caffeinate_proc = None
        self._obs_client = None
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def _set_status(self, text, finished=False):
        self.status_callback(text, finished)

    def _wait_until(self, target_time):
        """Wartet bis zur Zielzeit. Gibt False zurueck wenn abgebrochen."""
        while datetime.now() < target_time:
            if self._cancelled:
                self._set_status("Abgebrochen.", finished=True)
                return False
            remaining = target_time - datetime.now()
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            self._set_status(f"Warte auf Startzeit... noch {mins}m {secs}s")
            time.sleep(1)
        return True

    def _start_caffeinate(self, duration_seconds):
        """Verhindert, dass der Mac einschlaeft."""
        try:
            self._caffeinate_proc = subprocess.Popen(
                ["caffeinate", "-d", "-t", str(duration_seconds + 120)]
            )
            return True
        except FileNotFoundError:
            # Nicht macOS - kein caffeinate verfuegbar
            return True

    def _stop_caffeinate(self):
        if self._caffeinate_proc:
            self._caffeinate_proc.terminate()
            self._caffeinate_proc = None

    def _start_obs(self):
        """Startet OBS falls nicht bereits laufend."""
        try:
            subprocess.Popen(["open", "-a", "OBS"])
            return True
        except FileNotFoundError:
            self._set_status("Fehler: 'open' Befehl nicht gefunden. Laeuft dies auf macOS?", finished=True)
            return False

    def _connect_obs(self, password, max_retries=10):
        """Verbindet sich mit OBS WebSocket."""
        import obsws_python as obs

        for attempt in range(max_retries):
            if self._cancelled:
                return False
            try:
                self._obs_client = obs.ReqClient(
                    host="localhost", port=4455, password=password
                )
                return True
            except Exception:
                if attempt < max_retries - 1:
                    self._set_status(
                        f"OBS-Verbindung... Versuch {attempt + 2}/{max_retries}"
                    )
                    time.sleep(3)

        self._set_status(
            "Fehler: Konnte keine Verbindung zu OBS herstellen. "
            "Ist OBS gestartet und der WebSocket-Server aktiviert?",
            finished=True,
        )
        return False

    def _open_netflix(self, netflix_url):
        """Oeffnet Netflix in Chrome mit deaktivierter GPU."""
        # URL normalisieren
        url = netflix_url.strip()
        if not url.startswith("http"):
            # Relative URL -> vollstaendige URL
            if not url.startswith("/"):
                url = "/" + url
            url = "https://www.netflix.com" + url

        # /title/XXXXX -> /watch/XXXXX fuer direktes Abspielen (immer konvertieren)
        url = url.replace("/title/", "/watch/")

        try:
            subprocess.Popen([
                "open", "-a", "Google Chrome", "--args",
                "--disable-gpu", url
            ])
            return True
        except FileNotFoundError:
            self._set_status("Fehler: Chrome konnte nicht geoeffnet werden.", finished=True)
            return False

    def _auto_play(self):
        """Drueckt Leertaste in Chrome um Netflix-Wiedergabe zu starten."""
        try:
            subprocess.run(["osascript", "-e",
                'tell application "Google Chrome" to activate'])
            time.sleep(1)
            subprocess.run(["osascript", "-e",
                'tell application "System Events" to key code 49'])
        except FileNotFoundError:
            pass  # Nicht macOS - osascript nicht verfuegbar

    def _notify_finished(self, message):
        """Zeigt eine macOS-Benachrichtigung an."""
        try:
            subprocess.run(["osascript", "-e",
                f'display notification "{message}" with title "Netflix Aufnahme-Planer"'])
        except FileNotFoundError:
            pass  # Nicht macOS

    def run(self, netflix_url, start_time, duration_minutes, obs_password=""):
        """
        Hauptworkflow - laeuft im Background-Thread.

        Args:
            netflix_url: Netflix URL (z.B. /title/82157128 oder vollstaendige URL)
            start_time: datetime oder None fuer sofortigen Start
            duration_minutes: Aufnahmedauer in Minuten
            obs_password: OBS WebSocket Passwort
        """
        try:
            self._cancelled = False
            duration_seconds = int(duration_minutes * 60)

            # 1. Warten bis Startzeit (falls geplant)
            if start_time and start_time > datetime.now():
                self._set_status(f"Aufnahme geplant fuer {start_time.strftime('%H:%M')}")
                if not self._wait_until(start_time):
                    return

            if self._cancelled:
                self._set_status("Abgebrochen.", finished=True)
                return

            # 2. caffeinate starten
            self._set_status("Schlafmodus wird deaktiviert...")
            self._start_caffeinate(duration_seconds)

            # 3. OBS starten
            self._set_status("OBS wird gestartet...")
            if not self._start_obs():
                self._stop_caffeinate()
                return

            # 4. OBS WebSocket verbinden (mit Wartezeit fuer OBS-Start)
            self._set_status("Verbinde mit OBS...")
            time.sleep(5)
            if not self._connect_obs(obs_password):
                self._stop_caffeinate()
                return

            if self._cancelled:
                self._set_status("Abgebrochen.", finished=True)
                self._stop_caffeinate()
                return

            # 5. Netflix oeffnen
            self._set_status("Netflix wird geoeffnet...")
            if not self._open_netflix(netflix_url):
                self._stop_caffeinate()
                return

            # 6. Warten bis Seite geladen + Auto-Play
            self._set_status("Warte auf Netflix (10 Sekunden)...")
            time.sleep(10)
            self._set_status("Starte Wiedergabe...")
            self._auto_play()
            time.sleep(2)

            if self._cancelled:
                self._set_status("Abgebrochen.", finished=True)
                self._stop_caffeinate()
                return

            # 7. Aufnahme starten
            self._set_status("Aufnahme wird gestartet...")
            try:
                self._obs_client.start_record()
            except Exception as e:
                self._set_status(f"Fehler beim Starten der Aufnahme: {e}", finished=True)
                self._stop_caffeinate()
                return

            # 8. Fuer Dauer warten
            start = datetime.now()
            end = start + timedelta(seconds=duration_seconds)
            while datetime.now() < end:
                if self._cancelled:
                    break
                elapsed = (datetime.now() - start).total_seconds()
                remaining = duration_seconds - elapsed
                mins_left = int(remaining // 60)
                secs_left = int(remaining % 60)
                mins_total = int(elapsed // 60)
                self._set_status(
                    f"Aufnahme laeuft... {mins_total}m aufgenommen, "
                    f"noch {mins_left}m {secs_left}s"
                )
                time.sleep(1)

            # 9. Aufnahme stoppen
            self._set_status("Aufnahme wird gestoppt...")
            try:
                self._obs_client.stop_record()
            except Exception:
                pass  # Aufnahme war evtl. schon gestoppt

            # 10. Aufraeumen
            self._stop_caffeinate()

            if self._cancelled:
                self._set_status("Aufnahme abgebrochen und gestoppt.", finished=True)
                self._notify_finished("Aufnahme abgebrochen.")
            else:
                self._set_status(
                    f"Aufnahme fertig! ({duration_minutes} Minuten aufgenommen)",
                    finished=True,
                )
                self._notify_finished("Aufnahme fertig!")

        except Exception as e:
            self._stop_caffeinate()
            self._set_status(f"Unerwarteter Fehler: {e}", finished=True)
            self._notify_finished(f"Fehler: {e}")
