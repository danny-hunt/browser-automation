
import os
from typing import Optional
import openai
from dotenv import load_dotenv

from htmlstring import hackernews_login_html, hackernews_home_html, hackernew_submit_html
load_dotenv()

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")


def prompt(user_message: str):
    return f"""
Please respond with only javascript code that can be executed in the browser console that will fulfil this objective:
{user_message}
The code should not do anything other than fulfil that objective.
Do not respond with anything other than code. There should be no explanation of the code. Any text that is not valid javascript code will be rejected.
The username is {username} and the password is {password}.
The current page in html is the following:"""

login_prompt = f"I want to login. My username is {username} and my password is {password}."

scroll_prompt = "I want to scroll to the bottom of the page."


def process_output(output_message: str) -> str:
    message = output_message.replace("\\", "")
    if "```" in message:
        message = message.split("```")[1]
    elif "`" in message:
        message = message.split("`")[1]
    return message.strip()

def query(user_message: str, html: Optional[str]):
    print("===")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system", 
                "content": prompt(user_message)
            }, 
            {
                "role": "user",
                "content": str(html)
            }
        ],
        temperature=0,
        max_tokens=150,
    )
    print(process_output(response["choices"][0]["message"]["content"]))


audio_file = "./audio_files/submit.m4a"
def voice_to_text(file_name: str) -> str:
    print("=== voice attempt now ===")
    with open(file_name, "rb") as audio:
        transcript = openai.Audio.transcribe("whisper-1", audio)["text"]
    print(f'Audio clip transcribed as: "{transcript}"')
    return transcript


# """
query(f"I want to login. My username is {username} and my password is {password}.", hackernews_login_html)

query("I want to scroll to the bottom of the page.", None)

query("I want to go to the post creation page.", hackernews_home_html)

query(
    "I want to fill in the title and description fields. I want to tell the readers of hackernews that this post is the culmanation of my work at a hackathon in London.", 
    hackernew_submit_html
)

query(
    "I want to click the submit button", # This prompt at the moment has to be super specific since we don't update the html after the previous step
    hackernew_submit_html
)

query(
    voice_to_text(audio_file),
    hackernew_submit_html
)

