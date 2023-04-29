import os
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from uuid import uuid4

from main import query, voice_to_text

class PromptInput(BaseModel):
    message: str
    json: dict
    html: str


app = FastAPI()

@app.post("/prompt")
def hello(input: PromptInput):
    """
    Takes a prompt (goal to complete on the current webpage) and the current page's html.
    It returns some js to run that will complete that goal if run in the browser console.
    """
    output = query(input.message, input.html)
    return output


@app.post("/audio")
async def audio(audio_file: UploadFile, html: str):
    """
    Call this for example by doing 
    requests.post("/audio", files={"audio_file": audio_file}, data={"text_param": text_param})
    """
    audio_contents = await audio_file.file.read()
    uuid = uuid4()
    file_name = os.path.join("audio_files", f"{uuid}.m4a")
    with open(file_name, 'wb') as f:
        f.write(audio_contents)
    output = query(voice_to_text(file_name), html)
    return output
