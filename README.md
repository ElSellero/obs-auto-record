# 🎬 OBS Auto-Record

Automatically record Netflix streams with OBS Studio on macOS. Schedule recordings for later or start immediately — perfect for capturing live events you want to watch on your own time.

**Example:** The NFL game kicks off at 2:30 AM your time? Schedule a recording, go to sleep, and watch the full game tomorrow morning — spoiler-free.

## ⚙️ How It Works

You provide a Netflix URL, set a start time and duration, and the app handles the rest:

1. **Waits** for the scheduled start time (or starts immediately)
2. **Launches OBS** and connects via WebSocket
3. **Opens Netflix** in Chrome with `--disable-gpu` (prevents DRM black screen)
4. **Auto-plays** the content (`/watch/` URL triggers playback automatically)
5. **Enters fullscreen** (sends `F` key to Netflix)
6. **Starts recording** via OBS
7. **Records** for the configured duration with a live progress bar
8. **Stops recording** when time is up
9. **Exits fullscreen** and **closes the Netflix tab** (no audio leaking afterwards)
10. **Prevents sleep** throughout the entire process (`caffeinate`)

The web UI updates live, shows the current phase, and lets you cancel at any time.

## 📋 Requirements

- macOS (Apple Silicon or Intel)
- Google Chrome
- OBS Studio
- Internet connection

## 🛠️ Setup

### 1. Install dependencies

Open Terminal and run:

```bash
cd obs-auto-record
bash setup.sh
```

This installs Homebrew (if needed), Python, OBS, Chrome, and the Python packages. It also sets the correct file permissions so `start.command` can be launched from Finder.

### 2. Configure OBS Studio

1. **Open OBS**
2. **Create a Scene:** Click `+` under "Scenes" (bottom left)
3. **Add Display Capture:**
   - Click `+` under "Sources"
   - Choose "Display Capture" (or "macOS Screen Capture")
   - Click OK
4. **Enable WebSocket Server:**
   - Menu: Tools > WebSocket Server Settings
   - Check "Enable WebSocket Server"
   - Note the password (you'll need it in the app)
   - Click OK
5. **Set recording format:**
   - Menu: Settings (or OBS > Preferences)
   - Tab: "Output"
   - Recording Format: **mp4**
   - Click OK
6. **Allow Screen Recording:**
   - macOS will prompt on first use
   - System Settings > Privacy & Security > Screen Recording > enable OBS

### 3. Desktop Audio (Apple Silicon Macs)

macOS doesn't allow direct audio capture by default. To record Netflix audio along with the video, you need a virtual audio device.

Follow the official OBS guide to set up desktop audio capture using the **VB-Cable** plugin:

**[macOS Desktop Audio Capture Guide](https://obsproject.com/kb/macos-desktop-audio-capture-guide)**

Without this, your recordings will have video but no sound.

> ⚠️ **Important:** Since this is a desktop audio capture, your Mac's volume level matters! If you mute your system audio, the recording will have no sound either. Make sure the volume is set to an audible level before starting the recording.

### 4. Prepare Chrome

1. Open Google Chrome
2. Go to netflix.com and log in
3. Select the correct Netflix profile
4. Chrome can be closed afterwards — the app will reopen it automatically

## 🚀 Usage

### Start the app

Double-click **`start.command`** in Finder.

(First time: right-click > Open, since macOS blocks unknown scripts.)

If the file won't open at all, run `bash setup.sh` again — it sets the required permissions.

A terminal window opens and Chrome shows the recording interface.

### Set up a recording

1. **Netflix URL:** Paste the link to the show or event
   - From Chrome's address bar (e.g. `https://www.netflix.com/title/82157128`)
   - Or just the path: `/title/82157128`
   - `/title/` URLs are automatically converted to `/watch/` for direct playback
2. **Mode:** "Start now" or set a schedule time
3. **Duration:** How long to record (in minutes)
4. **OBS Password:** The password from OBS WebSocket settings
5. **Click the button** and you're done!

### During recording

- **Keep the MacBook lid open** (don't close it!)
- Don't close the terminal window
- Sleep mode is automatically prevented

### When recording finishes

- OBS stops recording
- Netflix exits fullscreen and the tab closes automatically
- The web UI shows the completion status

## 📂 Where are the recordings?

OBS saves recordings to the path configured in Settings > Output > Recording Path.

Default: `~/Movies` or `~/Videos`

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `start.command` won't open | Run `bash setup.sh` to fix permissions, or right-click > Open |
| OBS connection failed | Start OBS manually, check WebSocket server is enabled |
| Black screen in recording | Check Screen Recording permission for OBS in System Settings |
| Netflix shows black video | Chrome is launched with `--disable-gpu` automatically; make sure Chrome was fully closed before starting |
| Mac goes to sleep | Keep lid open, connect power adapter |
| Recording doesn't start | Check OBS WebSocket password |
| No audio in recording | Set up VB-Cable for desktop audio: [OBS guide](https://obsproject.com/kb/macos-desktop-audio-capture-guide) |
| Audio recorded but silent | Make sure your Mac volume is not muted — desktop capture records what you hear |

## 🧰 Tech Stack

- **[Streamlit](https://streamlit.io/)** — Web UI with live-updating status
- **[obsws-python](https://github.com/aatikturk/obsws-python)** — OBS WebSocket control
- **osascript** — macOS automation (fullscreen, tab close)
- **caffeinate** — Prevents macOS sleep during recording

## 📄 License

MIT
