
import json
import os
from time import sleep
from typing import Optional
import openai
from dotenv import load_dotenv
from selenium import webdriver
from pydub import AudioSegment
from pydub.playback import play

from htmlstring import hackernews_login_html, hackernews_home_html, hackernew_submit_html
load_dotenv()

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

chrome_options = webdriver.ChromeOptions()
DRIVER: Optional[webdriver.Chrome] = None 


def prompt(goal: str, events: Optional[list[str]]):
    events_string = '\n'.join([json.dumps(event) for event in events]) if events else ''
    return f"""
Please respond with only javascript code that can be executed in the browser console that will fulfil this objective:
{goal}
The code should not do anything other than fulfil that objective.
Do not respond with anything other than code. There should be no explanation of the code. Any text that is not valid javascript code will be rejected.
{'Here are some events that occurred the last time we visited this page:' if events else ''}
{events_string}
The html is included too"""


def create_chat_completion_messages(user_message: str, events: Optional[list[str]], html: Optional[str]) -> list[dict]:
    return [
        {
            "role": "system", 
            "content": prompt(user_message, events)
        }, 
        {
            "role": "user",
            "content": "Please do the above"
        }
    ]

login_prompt = f"I want to login. My username is {username} and my password is {password}."

scroll_prompt = "I want to scroll to the bottom of the page."


def process_output(output_message: str) -> str:
    message = output_message.replace("\\", "")
    if "```" in message:
        message = message.split("```")[1]
    elif "`" in message:
        message = message.split("`")[1]
    message = message.strip()
    message = "\n".join([line for line in message.split("\n") if "javascript" not in line.lower()])
    if DRIVER:
        try:
            DRIVER.execute_script(message)
        except Exception as e:
            print("failed to execute this code: \n" + message)
            print(f"occurred on this page: {DRIVER.find_element('tag name', 'body').get_attribute('innerHTML')}")
            # print(e)
            raise e
    return message

def query(user_message: str, events: Optional[list[str]], html: Optional[str]):
    print("===")
    if user_message == '':
        user_message = json.loads(events)[0]["text"]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=create_chat_completion_messages(user_message, events or [], html),
            temperature=0,
            max_tokens=150,
        )
    except Exception as e:
        if DRIVER:
            innerHTML = DRIVER.find_element('tag name', 'body').get_attribute('innerHTML')
            print(f"{innerHTML[:100]}")
            print(f"failed on this page: {DRIVER.find_element('tag name', 'body').get_attribute('innerHTML')[:100]}")
        raise e
    processed_output = process_output(response["choices"][0]["message"]["content"])
    print(processed_output)
    return processed_output


audio_file = "./audio_files/submit.m4a"
def voice_to_text(file_name: str) -> str:
    with open(file_name, "rb") as audio:
        transcript: str = openai.Audio.transcribe("whisper-1", audio)["text"]
    
    transcript = transcript.replace('username is username', f'username is {username}')
    transcript = transcript.replace('password is password', f'password is {password}')
    print(f'** Audio instructions transcribed as: "{transcript}"')
    return transcript


def dummy_procedure():
    DRIVER.get('https://news.ycombinator.com/news')
    query("I want to go to the hackernews login page.", [], hackernews_home_html)
    query(f"I want to login on this page. My username is {username} and my password is {password}.", [], hackernews_login_html)
    query("I want to scroll to the bottom of the page.", [], None)
    query("I want to go to the post creation page.", [], hackernews_home_html)
    query(
        "I want to fill in the title and description fields. \
        The information should relate to my desire to tell the readers of hackernews that this post is the culmanation of our work at a hackathon in London.\
        Do not submit the post yet.", 
        [],
        hackernew_submit_html
    )
    sleep(4)
    # query(
    #     "I want to click the submit button", # This prompt at the moment has to be super specific since we don't update the html after the previous step
    #     hackernew_submit_html
    # )

    # query(
    #     voice_to_text(audio_file),
    #     hackernew_submit_html
    # )

# """

if __name__ == "__main__":
    SEEN_FILES = set()
    # for file_name in os.listdir("./audio_files"):
    #     SEEN_FILES.add(file_name)

    DRIVER = webdriver.Chrome(chrome_options=chrome_options)
    print(sorted(os.listdir("./audio_files")))

    # dummy_procedure()
    while True:
        for file_name in filter(lambda x: x not in SEEN_FILES, sorted(os.listdir("./audio_files"))):
            fuller_path = os.path.join('audio_files', file_name)
            audio = AudioSegment.from_file(fuller_path, format="m4a")
            play(audio)
            query(
                voice_to_text(fuller_path),
                [],
                DRIVER.find_element("tag name", "body").get_attribute('innerHTML')[:3000]
            )
            print("===")
            SEEN_FILES.add(file_name)
        sleep(1)



