#!/bin/bash
# Einmalige Einrichtung fuer OBS Auto-Record
# Dieses Script im Terminal ausfuehren: bash setup.sh

set -e

echo "=== OBS Auto-Record - Einrichtung ==="
echo ""

# Homebrew pruefen/installieren
if ! command -v brew &> /dev/null; then
    echo "Homebrew wird installiert..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # M1/M2 Mac: Homebrew Pfad hinzufuegen
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo "Homebrew ist bereits installiert."
fi

# Python3 pruefen/installieren
if ! command -v python3 &> /dev/null; then
    echo "Python3 wird installiert..."
    brew install python3
else
    echo "Python3 ist bereits installiert: $(python3 --version)"
fi

# OBS Studio pruefen
if [ ! -d "/Applications/OBS.app" ]; then
    echo ""
    echo "HINWEIS: OBS Studio ist nicht installiert."
    echo "Bitte lade OBS Studio herunter: https://obsproject.com/download"
    echo "Oder installiere es mit: brew install --cask obs"
    read -p "OBS jetzt mit Homebrew installieren? (j/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        brew install --cask obs
    fi
else
    echo "OBS Studio ist installiert."
fi

# Firefox pruefen
if [ ! -d "/Applications/Firefox.app" ]; then
    echo ""
    echo "HINWEIS: Firefox ist nicht installiert."
    echo "Bitte lade Firefox herunter: https://www.mozilla.org/firefox/"
    echo "Oder installiere es mit: brew install --cask firefox"
    read -p "Firefox jetzt mit Homebrew installieren? (j/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        brew install --cask firefox
    fi
else
    echo "Firefox ist installiert."
fi

# Python-Abhaengigkeiten installieren
echo ""
echo "Python-Pakete werden installiert..."
cd "$(dirname "$0")"
pip3 install -r requirements.txt

# start.command ausfuehrbar machen
chmod +x start.command

echo ""
echo "=== Einrichtung abgeschlossen! ==="
echo ""
echo "Naechste Schritte:"
echo "1. OBS Studio oeffnen"
echo "2. Eine Scene mit 'Display Capture' erstellen"
echo "3. Tools > WebSocket Server Settings:"
echo "   - 'Enable WebSocket Server' aktivieren"
echo "   - Passwort merken (wird in der App benoetigt)"
echo "4. Aufnahmeformat auf MP4 einstellen:"
echo "   - Settings > Output > Recording Format: mp4"
echo "5. Firefox oeffnen und bei Netflix einloggen"
echo "6. Das richtige Netflix-Profil auswaehlen"
echo "7. Zum Starten: 'Start Aufnahme.command' doppelklicken"
echo ""
