from fastapi import FastAPI
from pydantic import BaseModel

from main import query

class PromptInput(BaseModel):
    prompt: str
    html: str



app = FastAPI()

@app.get("/prompt")
def hello(prompt: str, html: str):
    output = query(prompt, html)
    return output