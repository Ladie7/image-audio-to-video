from flask import Flask, request, jsonify
import subprocess
import os
import uuid
app = Flask(__name__)
@app.route('/')
def home():
    return '''
    <h1>🧠 Image + Audio to Video Converter</h1>
    <p>POST to <code>/convert</code> with JSON containing <code>image_url</code> and <code>audio_url</code> to generate a video.</p>
    '''


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
   "ffmpeg",
    "-loop", "1",
    "-i", image_file,
    "-i", audio_file,
    "-filter_complex",
    "[0:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1[fg];"  # foreground
    "[0:v]scale=720:1280:force_original_aspect_ratio=increase,boxblur=10:1,crop=720:1280[bg];"  # blurred background
    "[bg][fg]overlay=(W-w)/2:(H-h)/2",  # combine them
    "-c:v", "libx264",
    "-tune", "stillimage",
    "-c:=a", "aac",
    "-b=a", "192k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    output_name
]
    subprocess.run(cmd)

    return jsonify({"status": "success", "video_path": output_name})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    

