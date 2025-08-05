from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import requests
import subprocess
import os

app = FastAPI()

# Serve /static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/convert")
async def convert(request: Request):
    data = await request.json()
    image_url = data["image_url"]
    audio_url = data["audio_url"]
    output_name = data["output_name"]
    output_path = f"static/{output_name}"

    # Ensure static/ folder exists
    os.makedirs("static", exist_ok=True)

    # Download image
    image_path = "temp_image.png"
    with open(image_path, "wb") as f:
        f.write(requests.get(image_url).content)

    # Download audio
    audio_path = "temp_audio.mp3"
    with open(audio_path, "wb") as f:
        f.write(requests.get(audio_url).content)

    # Use FFmpeg to create video
    subprocess.run([
        "ffmpeg", "-loop", "1", "-i", image_path,
        "-i", audio_path, "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
    ])

    # Clean up
    os.remove(image_path)
    os.remove(audio_path)

    return {
        "status": "success",
        "video_url": f"https://image-audio-to-video.onrender.com/static/{output_name}"
    }
