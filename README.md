# 🚗 YT Music Downloader

This script lets you download a single YouTube/YT Music video as an MP3 or grab an entire playlist in one go. It’s built specifically to handle large batches (like a 500-song SuperMix).

## 🛠️ System Requirements

Before setting up the Python environment, ensure these system-level dependencies are installed on your macOS.

1. External Dependencies
   - FFmpeg: Handles the conversion of video streams into high-quality MP3s.

   - Node.js (via NVM): Required for yt-dlp to solve YouTube's "n-challenge" JavaScript signatures.

   ```Bash

   # Install Homebrew (if not present)

   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Install FFmpeg

   brew install ffmpeg

   # Install NVM and Node.js

   brew install nvm
   mkdir ~/.nvm
   nvm install node
   nvm use node
   ```

## 🚀 Installation & Provisioning

Follow these steps in order to initialize the environment and authorize the necessary downloader components.

1. Initialize Virtual Environment
   ```Bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Provision Remote Components (Crucial)
   YouTube frequently updates its signature algorithms. You must explicitly authorize the external JavaScript solver and clear the local cache to ensure a clean handshake.

   ```Bash

   # Download and trust the EJS solver

   python3 -m yt_dlp --remote-components ejs:github --update

   # Clear stale session data

   python3 -m yt_dlp --rm-cache-dir
   ```

## 📖 Usage

1. Launch the Orchestrator:

   ```Bash
   python3 main.py
   ```

2. Input URL: Paste a YouTube Music Playlist or Song URL when prompted.

3. Guest Mode Logic: The script automatically utilizes ios and android client signatures to bypass the "Access Error" blocks common on desktop web requests.

4. Idempotency Check: The script scans the downloads/ folder and will automatically skip any tracks that have already been processed.

## 📁 USB Formatting Guide

For maximum compatibility with vehicle infotainment systems, use Disk Utility with these settings:

- Format: MS-DOS (FAT) / FAT32

- Scheme: Master Boot Record (MBR)

- File Sanitization: The script automatically strips illegal characters (\ / \* ? : " < > |) to ensure seamless writes to the FAT32 filesystem.

## 🔧 Technical Overview

- Metadata Tagging: Uses mutagen to inject ID3 tags (Title, Artist) and embed Album Art.

- Image Processing: Automatically converts .webp thumbnails to .jpg for legacy car display compatibility.

- Failure Tolerance: Wrapped in try/except blocks so that DRM-protected or restricted tracks are logged as 🚫 SKIPPING without interrupting the 500-song queue.

### Pro-Tip

If you experience a sudden wave of 🚫 FAILED messages, it usually means your IP has been throttled. Running `python3 -m yt_dlp --rm-cache-dir` again or switching your network/VPN usually resolves the handshake block.

# ⚖️ Disclaimer

This project was created for educational purposes. Please use it responsibly and in compliance with YouTube's Terms of Service.
