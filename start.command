#!/bin/bash
cd "$(dirname "$0")"

clear
echo ""
echo "🎬  Netflix Aufnahme-Planer"
echo "══════════════════════════════════════════════════"
echo ""
echo "📋  Checkliste - bitte vorher pruefen:"
echo ""
echo "  💻  MacBook"
echo "      ├─ 🔌  Am Ladekabel angeschlossen"
echo "      └─ 📖  Deckel offen lassen (nicht zuklappen!)"
echo ""
echo "  🎥  OBS Studio"
echo "      ├─ ✅  OBS ist installiert und einmal gestartet"
echo "      ├─ 🖥️   Eine Scene mit 'Display Capture' erstellt"
echo "      ├─ 🔗  WebSocket Server aktiviert"
echo "      │      (Tools > WebSocket Server Settings > Enable)"
echo "      ├─ 🔑  WebSocket-Passwort gemerkt"
echo "      └─ 🎞️   Aufnahmeformat auf MP4 gestellt"
echo "             (Settings > Output > Recording Format: mp4)"
echo ""
echo "  🌐  Google Chrome"
echo "      ├─ ✅  Chrome ist installiert"
echo "      ├─ 🔐  Bei Netflix eingeloggt (netflix.com)"
echo "      └─ 👤  Das richtige Netflix-Profil ausgewaehlt"
echo ""
echo "  🔒  macOS-Berechtigungen"
echo "      └─ 🖥️   Bildschirmaufnahme fuer OBS erlaubt"
echo "             (Systemeinstellungen > Datenschutz"
echo "              > Bildschirmaufnahme > OBS)"
echo ""
echo "══════════════════════════════════════════════════"
echo "🚀  App wird gestartet..."
echo "    (Browser oeffnet sich gleich)"
echo ""

# Homebrew-Pfad fuer M1/M2 Macs
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Chrome mit der App oeffnen (nach kurzer Wartezeit fuer Streamlit-Start)
(sleep 3 && open -a "Google Chrome" http://localhost:8501) &

python3 -m streamlit run app.py \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.port=8501
