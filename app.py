"""OBS Auto-Record - Streaming Recording Scheduler."""

import re
import threading
from datetime import datetime, time

import streamlit as st

from recorder import Recorder

st.set_page_config(page_title="OBS Auto-Record", page_icon="🎬", layout="centered")

# --- Session State ---
if "recorder" not in st.session_state:
    st.session_state.recorder = None
if "recording_config" not in st.session_state:
    st.session_state.recording_config = None
if "balloons_shown" not in st.session_state:
    st.session_state.balloons_shown = False


def validate_netflix_url(url):
    url = url.strip()
    if not url:
        return False
    if re.match(r"^/?(title|watch)/\d+", url):
        return True
    if re.match(r"^https?://(www\.)?netflix\.com/", url):
        return True
    return False


# --- UI ---
st.title("OBS Auto-Record")
st.markdown("Schedule and record Netflix streams automatically with OBS.")

if st.session_state.recorder is None:
    mode = st.radio(
        "When to start?",
        ["Start now", "Schedule"],
        horizontal=True,
    )

    with st.form("recording_form"):
        netflix_url = st.text_input(
            "Netflix URL",
            placeholder="/title/82157128 or https://www.netflix.com/watch/...",
            help="Copy the URL of the Netflix show from your browser.",
        )

        scheduled_time = st.time_input(
            "Start time",
            value=time(20, 0),
            step=60,
            help="Scheduled start time (to the minute).",
            disabled=(mode == "Start now"),
        )

        duration = st.number_input(
            "Duration (minutes)",
            min_value=1,
            max_value=480,
            value=120,
            step=1,
            help="How long should the recording last?",
        )

        obs_password = st.text_input(
            "OBS WebSocket Password",
            type="password",
            help="Found in OBS: Tools > WebSocket Server Settings.",
        )

        submitted = st.form_submit_button(
            "Start recording" if mode == "Start now" else "Schedule recording",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not validate_netflix_url(netflix_url):
            st.error("Please enter a valid Netflix URL (e.g. /title/82157128).")
        else:
            start_time = None
            if mode == "Schedule":
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


# --- Status display (fragment updates every 1s without page flicker) ---
@st.fragment(run_every="1s")
def status_fragment():
    rec = st.session_state.recorder
    if rec is None:
        return

    config = st.session_state.recording_config or {}
    status_text = rec.status_text or "Preparing..."

    if not rec.is_finished:
        if st.button("Cancel recording", use_container_width=True):
            rec.cancel()

    st.divider()

    # Recording details
    details = f"**URL:** `{config.get('url', '')}`"
    if config.get("start_time"):
        details += f"  \n**Start time:** {config['start_time']}"
    details += f"  \n**Duration:** {config.get('duration', '')} min"
    st.markdown(details)

    # Phase + Status
    if not rec.is_finished:
        if "Waiting for start" in status_text or "Scheduled for" in status_text:
            st.info(f":clock1: {status_text}")
        elif "Recording..." in status_text:
            st.warning(f":red_circle: {status_text}")
            match = re.search(r"(\d+)m recorded, (\d+)m (\d+)s left", status_text)
            if match:
                elapsed = int(match.group(1)) * 60
                remaining = int(match.group(2)) * 60 + int(match.group(3))
                total = elapsed + remaining
                if total > 0:
                    st.progress(elapsed / total)
        else:
            st.info(f":gear: {status_text}")
    else:
        if "Error" in status_text or "Cancelled" in status_text:
            st.error(f":x: {status_text}")
        else:
            st.success(f":white_check_mark: {status_text}")
            if not st.session_state.balloons_shown:
                st.session_state.balloons_shown = True
                st.balloons()

        if st.button("New recording", type="primary", use_container_width=True):
            st.session_state.recorder = None
            st.session_state.recording_config = None
            st.rerun(scope="app")


status_fragment()
