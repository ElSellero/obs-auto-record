#!/bin/bash
# One-time setup for OBS Auto-Record
# Run in Terminal: bash setup.sh

set -e

echo "=== OBS Auto-Record - Setup ==="
echo ""

# Check/install Homebrew
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo "Homebrew is already installed."
fi

# Check/install Python3
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    brew install python3
else
    echo "Python3 is already installed: $(python3 --version)"
fi

# Check OBS Studio
if [ ! -d "/Applications/OBS.app" ]; then
    echo ""
    echo "NOTE: OBS Studio is not installed."
    echo "Download from: https://obsproject.com/download"
    echo "Or install with: brew install --cask obs"
    read -p "Install OBS with Homebrew now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install --cask obs
    fi
else
    echo "OBS Studio is installed."
fi

# Check Chrome
if [ ! -d "/Applications/Google Chrome.app" ]; then
    echo ""
    echo "NOTE: Google Chrome is not installed."
    echo "Download from: https://www.google.com/chrome/"
    echo "Or install with: brew install --cask google-chrome"
    read -p "Install Chrome with Homebrew now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install --cask google-chrome
    fi
else
    echo "Google Chrome is installed."
fi

# Install Python dependencies
echo ""
echo "Installing Python packages..."
cd "$(dirname "$0")"
pip3 install -r requirements.txt

# Make start.command executable
chmod +x start.command

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "1. Open OBS Studio"
echo "2. Create a Scene with 'Display Capture'"
echo "3. Tools > WebSocket Server Settings:"
echo "   - Enable 'WebSocket Server'"
echo "   - Note the password (needed in the app)"
echo "4. Set recording format to MP4:"
echo "   - Settings > Output > Recording Format: mp4"
echo "5. Open Google Chrome and log in to Netflix"
echo "6. Select the correct Netflix profile"
echo "7. To start: double-click 'start.command'"
echo ""
