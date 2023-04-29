
import os
from typing import Optional
import openai
from dotenv import load_dotenv

from htmlstring import hackernews_html
load_dotenv()

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")


def prompt(user_message: str):
    return f"""
Please respond with only javascript code that can be executed in the browser console that will fulfil this objective:
{user_message}
Do not respond with anything other than code. There should be no explanation of the code. Any text that is not valid javascript code will be rejected.
The username is {username} and the password is {password}.
The current page in html is the following:"""

login_prompt = f"I want to login. My username is {username} and my password is {password}."

scroll_prompt = "I want to scroll to the bottom of the page."

def query(user_message: str, html: Optional[str]):
    return openai.ChatCompletion.create(
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

def process_output(output_message: str) -> str:
    message = output_message.replace("\\", "")
    if "```" in message:
        message = message.split("```")[1]
    elif "`" in message:
        message = message.split("`")[1]
    return message.strip()


login_response = query(login_prompt, hackernews_html)
print(process_output(login_response["choices"][0]["message"]["content"]))

print ("===")

scroll = query(scroll_prompt, None)
print(process_output(scroll["choices"][0]["message"]["content"]))

