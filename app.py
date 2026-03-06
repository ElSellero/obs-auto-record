"""OBS Auto-Record - Netflix Aufnahme-Planer."""

import re
import threading
from datetime import datetime, time

import streamlit as st

from recorder import Recorder

st.set_page_config(page_title="Netflix Aufnahme-Planer", page_icon="🎬", layout="centered")

# --- Session State initialisieren ---
if "status_text" not in st.session_state:
    st.session_state.status_text = ""
if "is_finished" not in st.session_state:
    st.session_state.is_finished = False
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "recorder" not in st.session_state:
    st.session_state.recorder = None


def status_callback(text, finished):
    st.session_state.status_text = text
    st.session_state.is_finished = finished
    if finished:
        st.session_state.is_running = False


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
        help="Uhrzeit fuer den geplanten Start.",
        disabled=(mode == "Sofort starten"),
    )

    duration = st.number_input(
        "Dauer (Minuten)",
        min_value=1,
        max_value=480,
        value=120,
        step=10,
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
if submitted and not st.session_state.is_running:
    if not validate_netflix_url(netflix_url):
        st.error("Bitte eine gueltige Netflix-URL eingeben (z.B. /title/82157128).")
    else:
        # Startzeit berechnen
        start_time = None
        if mode == "Geplante Zeit":
            now = datetime.now()
            start_time = now.replace(
                hour=scheduled_time.hour,
                minute=scheduled_time.minute,
                second=0,
                microsecond=0,
            )
            # Wenn die Zeit heute schon vorbei ist, naechsten Tag nehmen
            if start_time <= now:
                from datetime import timedelta
                start_time += timedelta(days=1)

        st.session_state.is_running = True
        st.session_state.is_finished = False
        st.session_state.status_text = "Wird vorbereitet..."

        recorder = Recorder(status_callback)
        st.session_state.recorder = recorder

        thread = threading.Thread(
            target=recorder.run,
            args=(netflix_url, start_time, duration, obs_password),
            daemon=True,
        )
        thread.start()
        st.rerun()

# --- Status-Anzeige ---
if st.session_state.is_running or st.session_state.status_text:
    st.divider()

    if st.session_state.is_running:
        st.info(st.session_state.status_text or "Laeuft...")

        if st.button("Abbrechen", type="secondary"):
            if st.session_state.recorder:
                st.session_state.recorder.cancel()
            st.rerun()
    elif st.session_state.is_finished:
        status_text = st.session_state.status_text
        if "Fehler" in status_text or "Abgebrochen" in status_text:
            st.error(status_text)
        else:
            st.success(status_text)

        if st.button("Neue Aufnahme"):
            st.session_state.status_text = ""
            st.session_state.is_finished = False
            st.rerun()

# Auto-refresh waehrend Aufnahme laeuft
if st.session_state.is_running:
    import time as _time
    _time.sleep(1)
    st.rerun()
