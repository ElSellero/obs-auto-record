#!/bin/bash
# Doppelklick-Starter fuer macOS
# Oeffnet die Netflix Aufnahme-Planer Web-Oberflaeche

cd "$(dirname "$0")"

# Homebrew-Pfad fuer M1/M2 Macs
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

python3 -m streamlit run app.py \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.port=8501
