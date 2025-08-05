from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import requests
import subprocess
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Image-Audio-to-Video API is running"}

class MediaInput(BaseModel):
    image_url: str
    audio_url: str

@app.post("/convert")
async def convert(input: MediaInput):
    image_url = input.image_url
    audio_url = input.audio_url

    # Unique filenames
    uid = str(uuid.uuid4())
    image_file = f"static/{uid}_image.png"
    audio_file = f"static/{uid}_audio.mp3"
    output_file = f"static/{uid}_output.mp4"

    # Download image
    img_response = requests.get(image_url)
    with open(image_file, "wb") as f:
        f.write(img_response.content)

    # Download audio
    aud_response = requests.get(audio_url)
    with open(audio_file, "wb") as f:
        f.write(aud_response.content)

    # Convert to video using ffmpeg
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_file,
        "-i", audio_file,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-y", output_file
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Return video URL
    return {
        "video_url": f"https://image-audio-to-video.onrender.com/{output_file}"
    }

