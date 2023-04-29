from fastapi import FastAPI
from pydantic import BaseModel

from main import query

class PromptInput(BaseModel):
    prompt: str
    html: str


app = FastAPI()

@app.get("/prompt")
def hello(prompt: str, html: str):
    """
    Takes a prompt (goal to complete on the current webpage) and the current page's html.
    It returns some js to run that will complete that goal if run in the browser console.
    """
    output = query(prompt, html)
    return output