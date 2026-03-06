"""OBS Auto-Record - Netflix Aufnahme-Planer."""

import re
import threading
from datetime import datetime, time

import streamlit as st

from recorder import Recorder

st.set_page_config(page_title="Netflix Aufnahme-Planer", page_icon="🎬", layout="centered")

# --- Session State initialisieren ---
if "recorder" not in st.session_state:
    st.session_state.recorder = None
if "recording_config" not in st.session_state:
    st.session_state.recording_config = None
if "balloons_shown" not in st.session_state:
    st.session_state.balloons_shown = False


def validate_netflix_url(url):
    """Prueft ob die URL eine gueltige Netflix-URL ist."""
    url = url.strip()
    if not url:
        return False
    # Akzeptiert: /title/XXXXX, /watch/XXXXX, oder vollstaendige Netflix-URLs
    if re.match(r"^/?(title|watch)/\d+", url):
        return True
    if re.match(r"^https?://(www\.)?netflix\.com/", url):
        return True
    return False


# --- UI ---
st.title("Netflix Aufnahme-Planer")
st.markdown("Nimm Netflix-Sendungen automatisch mit OBS auf.")

if st.session_state.recorder is None:
    # --- Eingabe-Formular (nur wenn keine Aufnahme aktiv) ---
    mode = st.radio(
        "Wann starten?",
        ["Sofort starten", "Geplante Zeit"],
        horizontal=True,
    )

    with st.form("recording_form"):
        netflix_url = st.text_input(
            "Netflix URL",
            placeholder="/title/82157128 oder https://www.netflix.com/watch/...",
            help="Kopiere die URL der Netflix-Sendung aus dem Browser.",
        )

        scheduled_time = st.time_input(
            "Startzeit",
            value=time(20, 0),
            step=60,
            help="Uhrzeit fuer den geplanten Start (minutengenau).",
            disabled=(mode == "Sofort starten"),
        )

        duration = st.number_input(
            "Dauer (Minuten)",
            min_value=1,
            max_value=480,
            value=120,
            step=1,
            help="Wie lange soll aufgenommen werden?",
        )

        obs_password = st.text_input(
            "OBS WebSocket Passwort",
            type="password",
            help="Zu finden in OBS: Tools > WebSocket Server Settings.",
        )

        submitted = st.form_submit_button(
            "Aufnahme starten" if mode == "Sofort starten" else "Aufnahme planen",
            type="primary",
            use_container_width=True,
        )

    # --- Formular verarbeiten ---
    if submitted:
        if not validate_netflix_url(netflix_url):
            st.error("Bitte eine gueltige Netflix-URL eingeben (z.B. /title/82157128).")
        else:
            start_time = None
            if mode == "Geplante Zeit":
                now = datetime.now()
                start_time = now.replace(
                    hour=scheduled_time.hour,
                    minute=scheduled_time.minute,
                    second=0,
                    microsecond=0,
                )
                if start_time <= now:
                    from datetime import timedelta
                    start_time += timedelta(days=1)

            recorder = Recorder()
            st.session_state.recorder = recorder
            st.session_state.recording_config = {
                "url": netflix_url,
                "duration": duration,
                "start_time": start_time.strftime("%H:%M") if start_time else None,
            }
            st.session_state.balloons_shown = False

            thread = threading.Thread(
                target=recorder.run,
                args=(netflix_url, start_time, duration, obs_password),
                daemon=True,
            )
            thread.start()
            st.rerun()


# --- Status-Anzeige als Fragment (kein Flackern) ---
@st.fragment(run_every="1s")
def status_fragment():
    rec = st.session_state.recorder
    if rec is None:
        return

    config = st.session_state.recording_config or {}
    status_text = rec.status_text or "Wird vorbereitet..."

    # Abbrechen-Button (ersetzt den "Aufnahme planen"-Button)
    if not rec.is_finished:
        if st.button("Aufnahme abbrechen", use_container_width=True):
            rec.cancel()

    st.divider()

    # Aufnahme-Details
    details = f"**URL:** `{config.get('url', '')}`"
    if config.get("start_time"):
        details += f"  \n**Startzeit:** {config['start_time']}"
    details += f"  \n**Dauer:** {config.get('duration', '')} Min."
    st.markdown(details)

    # Phase + Status
    if not rec.is_finished:
        if "Warte auf Startzeit" in status_text or "geplant fuer" in status_text:
            st.info(f":clock1: {status_text}")
        elif "Aufnahme laeuft" in status_text:
            st.warning(f":red_circle: {status_text}")
            match = re.search(r"(\d+)m aufgenommen, noch (\d+)m (\d+)s", status_text)
            if match:
                elapsed = int(match.group(1)) * 60
                remaining = int(match.group(2)) * 60 + int(match.group(3))
                total = elapsed + remaining
                if total > 0:
                    st.progress(elapsed / total)
        else:
            st.info(f":gear: {status_text}")
    else:
        if "Fehler" in status_text or "Abgebrochen" in status_text:
            st.error(f":x: {status_text}")
        else:
            st.success(f":white_check_mark: {status_text}")
            if not st.session_state.balloons_shown:
                st.session_state.balloons_shown = True
                st.balloons()

        if st.button("Neue Aufnahme", type="primary", use_container_width=True):
            st.session_state.recorder = None
            st.session_state.recording_config = None
            st.rerun(scope="app")


status_fragment()
