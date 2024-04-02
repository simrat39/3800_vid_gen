import shutil
from moviepy.editor import *
from moviepy.video.fx.all import crop
import requests
import json
import os
from fastapi import FastAPI, File, Form, UploadFile
from typing import Annotated, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/generate_video")
def generate_video(tts: List[UploadFile], script: Annotated[str, Form()]):
    print(script)
    print(tts)

    for file in tts:
        file_location = f"files/{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

    data = json.loads(script)
    clips = []
    idx = 0
    for line in data["content"]:
        print(line["sentence"])
        print(line["video"])

        # urllib.request.urlretrieve(line["video"], line["image_search_keyword"] + '.mp4')
        r = requests.get(line["video"])
        print(r)

        with open(line["image_search_keyword"] + ".mp4", "wb") as outfile:
            outfile.write(r.content)

        tts_clip = AudioFileClip("./files/tts" + str(idx) + ".mp3")
        audio_length = tts_clip.duration

        nclip = VideoFileClip(line["image_search_keyword"] + ".mp4").subclip(0, audio_length)
        nclip = nclip.resize((1080, 1920))
        nclip = nclip.volumex(0.0)

        nclip = nclip.set_audio(tts_clip)

        txt_clip = TextClip(
            line["sentence"],
            fontsize=75,
            color="white",
            font="Keep-Calm-Medium",
            size=(1080, 1920),
            method="caption",
            align="center",
            stroke_color="black",
            stroke_width=3,
        )
        txt_clip = txt_clip.set_pos("center").set_duration(audio_length)

        cmp_clip = CompositeVideoClip([nclip, txt_clip])

        clips.append(cmp_clip)
        idx = idx + 1

    combined = concatenate_videoclips(clips)
    # tts_clip = AudioFileClip("./files/tts.mp3")
    # combined = combined.set_audio(tts_clip)
    combined.write_videofile("combined.mp4")

    for line in data["content"]:
        os.remove(line["image_search_keyword"] + ".mp4")

    return FileResponse("./combined.mp4")
