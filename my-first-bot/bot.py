import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI


_ = load_dotenv(find_dotenv()) # read local .env file

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion.choices[0].message)