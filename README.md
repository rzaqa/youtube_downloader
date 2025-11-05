# 🎥 YouTube Video Downloader (GUI)

A simple **desktop application** for downloading YouTube videos with a graphical interface built using **Tkinter** and **yt-dlp**.

---

## 🚀 Features

- 🖱️ **User-friendly interface** (Tkinter-based)  
- 📥 **Download videos** in the best available MP4 format  
- 📊 **Real-time progress bar** and status updates  
- 🔗 Supports **single YouTube video URLs**  
- ✅ Uses the reliable **yt-dlp** backend  
- 🎨 Clean layout with **YouTube-style branding**

---

## 📦 Requirements

- Python 3.8+
- `yt-dlp`
- `Pillow` (for image handling)

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/rzaqa/youtube_downloader.git
cd youtube_downloader

## 🍏 macOS Build & Run

Prereqs:
- Python 3.10 (recommended) with Tkinter
- PyInstaller (see `requirements.txt`)
- `yt-dlp` binary placed at `app_binaries/yt-dlp` (required)
- `ffmpeg` binary at `app_binaries/ffmpeg` (optional but recommended for audio extraction)

Steps:
```bash
python3 -m venv down_venv
source down_venv/bin/activate
pip install -r requirements.txt
chmod +x app_binaries/yt-dlp
# Optional if present
chmod +x app_binaries/ffmpeg || true
./build_macos.sh
open "dist/YouTube Downloader.app"
```

Notes:
- If macOS shows “App is from an unidentified developer”, go to System Settings → Privacy & Security → Open Anyway.
- Audio extraction uses ffmpeg. If `app_binaries/ffmpeg` is not bundled, system `ffmpeg` must be available in PATH.
- For distribution, consider codesigning and notarization.

