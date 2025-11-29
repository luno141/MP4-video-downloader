from flask import Flask, request, jsonify
from flask_cors import CORS
from pytubefix import YouTube
from urllib.parse import urlparse, parse_qs
import re
import os

app = Flask(__name__)
CORS(app)
def extract_video_id(url):
    # Case 1: Full link: youtube.com/watch?v=xxxx
    if "watch" in url:
        query = parse_qs(urlparse(url).query)
        return query.get("v", ["unknown"])[0]

    # Case 2: youtu.be/xxxx
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]

    # Case 3: shorts/xxxx
    if "shorts" in url:
        return url.split("shorts/")[1].split("?")[0]

    # Case 4: embed/xxxx
    if "embed" in url:
        return url.split("embed/")[1].split("?")[0]

    return "unknown"
def download_video(url, resolution):
    try:
        yt = YouTube(url)
        video_id = extract_video_id(url)
        out_dir = os.path.join("downloads", video_id)
        os.makedirs(out_dir, exist_ok=True)
        output_file = os.path.join(out_dir, f"{yt.title}.mp4")

        # Try progressive first (video + audio)
        stream = yt.streams.filter(progressive=True, file_extension="mp4", resolution=resolution).first()
        if stream:
            stream.download(output_path=out_dir, filename=f"{yt.title}.mp4")
            return True, None

        # Otherwise, get video-only + audio-only
        video_stream = yt.streams.filter(file_extension="mp4", res=resolution, only_video=True).first()
        audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").order_by("abr").desc().first()

        if not video_stream or not audio_stream:
            return False, f"Resolution {resolution} not available."

        # Download video and audio separately
        video_path = os.path.join(out_dir, "video.mp4")
        audio_path = os.path.join(out_dir, "audio.mp4")
        video_stream.download(output_path=out_dir, filename="video.mp4")
        audio_stream.download(output_path=out_dir, filename="audio.mp4")

        # Merge using ffmpeg
        import subprocess
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            output_file
        ], check=True)

        # Remove temporary files
        os.remove(video_path)
        os.remove(audio_path)

        return True, None

    except Exception as e:
        return False, str(e)

     # Try progressive first (video+audio)
        

def get_video_info(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.first()
        video_info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": yt.publish_date,
        }
        return video_info, None
    except Exception as e:
        return None, str(e)


@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    
    success, error_message = download_video(url, resolution)
    
    if success:
        return jsonify({"message": f"Video with resolution {resolution} downloaded successfully."}), 200
    else:
        return jsonify({"error": error_message}), 500

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    
    video_info, error_message = get_video_info(url)
    
    if video_info:
        return jsonify(video_info), 200
    else:
        return jsonify({"error": error_message}), 500


@app.route('/available_resolutions', methods=['POST'])
def available_resolutions():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    
    try:
        yt = YouTube(url)
        progressive_resolutions = list(set([
            stream.resolution 
            for stream in yt.streams.filter(progressive=True, file_extension='mp4')
            if stream.resolution
        ]))
        all_resolutions = list(set([
            stream.resolution 
            for stream in yt.streams.filter(file_extension='mp4')
            if stream.resolution
        ]))
        return jsonify({
            "progressive": sorted(progressive_resolutions),
            "all": sorted(all_resolutions)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "YouTube Downloader API is running",
        "endpoints": {
            "POST /download/<resolution>": "Download video at specific resolution",
            "POST /video_info": "Get video details",
            "POST /available_resolutions": "List all resolutions"
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
