from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import requests

app = FastAPI()

# Serve the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/convert")
async def convert(request: Request):
    data = await request.json()
    image_url = data["image_url"]
    audio_url = data["audio_url"]
    output_name = data["output_name"]

    image_path = f"temp_image.png"
    audio_path = f"temp_audio.mp3"
    output_path = f"static/{output_name}"

    # Download image
    img_data = requests.get(image_url).content
    with open(image_path, "wb") as f:
        f.write(img_data)

    # Download audio
    audio_data = requests.get(audio_url).content
    with open(audio_path, "wb") as f:
        f.write(audio_data)

    # Generate video using FFmpeg
    command = [
        "ffmpeg", "-loop", "1", "-i", image_path, "-i", audio_path,
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
        "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", output_path
    ]
    subprocess.run(command)

    # Remove temp files
    os.remove(image_path)
    os.remove(audio_path)

    return {
        "status": "success",
        "video_url": f"https://image-audio-to-video.onrender.com/static/{output_name}"
    }
