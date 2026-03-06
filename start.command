#!/bin/bash
cd "$(dirname "$0")"

clear
echo ""
echo "🎬  OBS Auto-Record"
echo "══════════════════════════════════════════════════"
echo ""
echo "📋  Checklist - please verify before starting:"
echo ""
echo "  💻  MacBook"
echo "      ├─ 🔌  Plugged in to power"
echo "      └─ 📖  Keep the lid open (don't close it!)"
echo ""
echo "  🎥  OBS Studio"
echo "      ├─ ✅  Installed and launched at least once"
echo "      ├─ 🖥️   A Scene with 'Display Capture' set up"
echo "      ├─ 🔗  WebSocket Server enabled"
echo "      │      (Tools > WebSocket Server Settings > Enable)"
echo "      ├─ 🔑  WebSocket password noted"
echo "      └─ 🎞️   Recording format set to MP4"
echo "             (Settings > Output > Recording Format: mp4)"
echo ""
echo "  🌐  Google Chrome"
echo "      ├─ ✅  Chrome is installed"
echo "      ├─ 🔐  Logged in to Netflix (netflix.com)"
echo "      └─ 👤  Correct Netflix profile selected"
echo ""
echo "  🔒  macOS Permissions"
echo "      └─ 🖥️   Screen Recording allowed for OBS"
echo "             (System Settings > Privacy & Security"
echo "              > Screen Recording > OBS)"
echo ""
echo "══════════════════════════════════════════════════"
echo "🚀  Starting app..."
echo "    (Browser will open shortly)"
echo ""

# Homebrew path for M1/M2 Macs
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Open Chrome with the app (after a short delay for Streamlit to start)
(sleep 3 && open -a "Google Chrome" http://localhost:8501) &

python3 -m streamlit run app.py \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.port=8501
