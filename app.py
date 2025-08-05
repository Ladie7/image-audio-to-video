import subprocess
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uuid

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
    image_file = f"{uid}_image.png"
    audio_file = f"{uid}_audio.mp3"
    output_name = f"{uid}_output.mp4"

    # Download image and audio
    subprocess.run(["curl", "-o", image_file, image_url])
    subprocess.run(["curl", "-o", audio_file, audio_url])

    # Convert using FFmpeg with blurred background for 9:16 (Shorts)
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_file,
        "-i", audio_file,
        "-filter_complex",
        "[0:v]scale=720:1280:force_original_aspect_ratio=decrease,"
        "pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1[fg];"
        "[0:v]scale=720:1280:force_original_aspect_ratio=increase,"
        "boxblur=10:1,crop=720:1280[bg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:=a", "aac",
        "-b:=a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_name
    ]

    subprocess.run(cmd)

    return {"video_file": output_name}

