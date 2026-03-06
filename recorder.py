"""Core logic: scheduling, OBS control, Netflix automation."""

import subprocess
import time
from datetime import datetime, timedelta


class Recorder:
    """Controls the entire recording workflow."""

    def __init__(self):
        self.status_text = ""
        self.is_finished = False
        self._caffeinate_proc = None
        self._obs_client = None
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def _set_status(self, text, finished=False):
        self.status_text = text
        self.is_finished = finished

    def _wait_until(self, target_time):
        """Waits until the target time. Returns False if cancelled."""
        while datetime.now() < target_time:
            if self._cancelled:
                self._set_status("Cancelled.", finished=True)
                return False
            remaining = target_time - datetime.now()
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            self._set_status(f"Waiting for start time... {mins}m {secs}s left")
            time.sleep(1)
        return True

    def _start_caffeinate(self, duration_seconds):
        """Prevents the Mac from sleeping."""
        try:
            self._caffeinate_proc = subprocess.Popen(
                ["caffeinate", "-d", "-t", str(duration_seconds + 120)]
            )
            return True
        except FileNotFoundError:
            return True

    def _stop_caffeinate(self):
        if self._caffeinate_proc:
            self._caffeinate_proc.terminate()
            self._caffeinate_proc = None

    def _start_obs(self):
        """Launches OBS if not already running."""
        try:
            subprocess.Popen(["open", "-a", "OBS"])
            return True
        except FileNotFoundError:
            self._set_status("Error: 'open' command not found. Is this running on macOS?", finished=True)
            return False

    def _connect_obs(self, password, max_retries=10):
        """Connects to OBS WebSocket."""
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
                        f"Connecting to OBS... attempt {attempt + 2}/{max_retries}"
                    )
                    time.sleep(3)

        self._set_status(
            "Error: Could not connect to OBS. "
            "Is OBS running and the WebSocket server enabled?",
            finished=True,
        )
        return False

    def _open_netflix(self, netflix_url):
        """Opens Netflix in Chrome with GPU disabled."""
        url = netflix_url.strip()
        if not url.startswith("http"):
            if not url.startswith("/"):
                url = "/" + url
            url = "https://www.netflix.com" + url

        # /title/XXXXX -> /watch/XXXXX for direct playback
        url = url.replace("/title/", "/watch/")

        try:
            subprocess.Popen([
                "open", "-a", "Google Chrome", url,
                "--args", "--disable-gpu"
            ])
            return True
        except FileNotFoundError:
            self._set_status("Error: Could not open Chrome.", finished=True)
            return False

    def _send_key(self, key_code):
        """Sends a keypress to Chrome via osascript."""
        try:
            subprocess.run(["osascript", "-e",
                'tell application "Google Chrome" to activate'])
            time.sleep(0.5)
            subprocess.run(["osascript", "-e",
                f'tell application "System Events" to key code {key_code}'])
        except FileNotFoundError:
            pass

    def _close_netflix_tab(self):
        """Closes the active Chrome tab (Cmd+W)."""
        try:
            subprocess.run(["osascript", "-e",
                'tell application "Google Chrome" to activate'])
            time.sleep(0.5)
            subprocess.run(["osascript", "-e",
                'tell application "System Events" to keystroke "w" using command down'])
        except FileNotFoundError:
            pass

    def _notify_finished(self, message):
        """Shows a macOS notification."""
        try:
            subprocess.run(["osascript", "-e",
                f'display notification "{message}" with title "OBS Auto-Record"'])
        except FileNotFoundError:
            pass

    def run(self, netflix_url, start_time, duration_minutes, obs_password=""):
        """
        Main workflow - runs in a background thread.

        Args:
            netflix_url: Netflix URL (e.g. /title/82157128 or full URL)
            start_time: datetime or None for immediate start
            duration_minutes: Recording duration in minutes
            obs_password: OBS WebSocket password
        """
        try:
            self._cancelled = False
            duration_seconds = int(duration_minutes * 60)

            # 1. Wait for scheduled start time
            if start_time and start_time > datetime.now():
                self._set_status(f"Scheduled for {start_time.strftime('%H:%M')}")
                if not self._wait_until(start_time):
                    return

            if self._cancelled:
                self._set_status("Cancelled.", finished=True)
                return

            # 2. Prevent sleep
            self._set_status("Disabling sleep mode...")
            self._start_caffeinate(duration_seconds)

            # 3. Launch OBS
            self._set_status("Starting OBS...")
            if not self._start_obs():
                self._stop_caffeinate()
                return

            # 4. Connect to OBS WebSocket
            self._set_status("Connecting to OBS...")
            time.sleep(5)
            if not self._connect_obs(obs_password):
                self._stop_caffeinate()
                return

            if self._cancelled:
                self._set_status("Cancelled.", finished=True)
                self._stop_caffeinate()
                return

            # 5. Open Netflix
            self._set_status("Opening Netflix...")
            if not self._open_netflix(netflix_url):
                self._stop_caffeinate()
                return

            # 6. Wait for Netflix to load and auto-play (/watch/ URL)
            self._set_status("Waiting for Netflix to load (12s)...")
            time.sleep(12)

            # 7. Enter fullscreen (F key in Netflix)
            self._set_status("Entering fullscreen...")
            self._send_key(3)  # key code 3 = F key
            time.sleep(1)

            if self._cancelled:
                self._set_status("Cancelled.", finished=True)
                self._stop_caffeinate()
                return

            # 8. Start recording
            self._set_status("Starting recording...")
            try:
                self._obs_client.start_record()
            except Exception as e:
                self._set_status(f"Error starting recording: {e}", finished=True)
                self._stop_caffeinate()
                return

            # 9. Wait for duration
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
                    f"Recording... {mins_total}m recorded, "
                    f"{mins_left}m {secs_left}s left"
                )
                time.sleep(1)

            # 10. Stop recording
            self._set_status("Stopping recording...")
            try:
                self._obs_client.stop_record()
            except Exception:
                pass

            # 11. Exit fullscreen + close Netflix tab
            self._set_status("Closing Netflix...")
            self._send_key(3)  # F key -> exit fullscreen
            time.sleep(1)
            self._close_netflix_tab()

            # 12. Cleanup
            self._stop_caffeinate()

            if self._cancelled:
                self._set_status("Recording cancelled and stopped.", finished=True)
                self._notify_finished("Recording cancelled.")
            else:
                self._set_status(
                    f"Recording complete! ({duration_minutes} minutes recorded)",
                    finished=True,
                )
                self._notify_finished("Recording complete!")

        except Exception as e:
            self._stop_caffeinate()
            self._set_status(f"Unexpected error: {e}", finished=True)
            self._notify_finished(f"Error: {e}")
