# MP4-youtube-video-downloader
A lightweight YouTube MP4 downloader with a simple HTML frontend and a Python backend powered by yt-dlp.
Allows users to input a YouTube link, choose resolution, and download videos directly.

#FEATURES
Clean HTML UI for easy usage

Python backend that handles actual downloads

Download videos in MP4 format

Supports multiple resolutions (144p–1080p depending on availability)

Automatically fetches & saves using the video title

Files saved inside the downloads/ folder


MP4-video-downloader/
├── index.html          # Frontend UI
├── style.css           # Optional styling
├── script.js           # Sends request to Python backend
├── downloader.py       # Python backend
├── downloads/          # Output files
└── README.md

Install yt-dlp:
pip install yt-dlp

Install FLASK:
pip install flask

1️⃣ Start the Python backend

If using Flask:

python3 downloader.py


Backend will run on:

http://localhost:5000

2️⃣ Open the HTML UI

Open index.html in your browser:

Right-click > Open With > Browser

3️⃣ Use the downloader

Enter:

YouTube URL

Resolution (optional)

Then click Download MP4.


📥 Output Files

All downloaded videos are stored inside:

downloads/<video-title>.mp4


🛠️ How It Works

The HTML page sends a request to the Python backend

Python fetches metadata → selects best MP4 format → downloads

The file is renamed using the extracted title

Saved locally for the user



