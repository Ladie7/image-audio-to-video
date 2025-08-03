from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert_to_video():
    data = request.json
    image_url = data.get("image_url")
    audio_url = data.get("audio_url")
    output_name = data.get("output_name", f"video_{uuid.uuid4().hex}.mp4")

    # Save the inputs
    image_file = "image.jpg"
    audio_file = "audio.mp3"
    subprocess.run(["curl", "-o", image_file, image_url])
    subprocess.run(["curl", "-o", audio_file, audio_url])

    # Convert using FFmpeg
    cmd = [
        "ffmpeg", "-loop", "1", "-i", image_file, "-i", audio_file,
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
        "-b:a", "192k", "-shortest", output_name
    ]
    subprocess.run(cmd)

    return jsonify({"status": "success", "video_path": output_name})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
