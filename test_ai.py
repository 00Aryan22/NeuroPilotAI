from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-3.5-turbo",

    messages=[
        {
            "role": "user",
            "content": "Explain AI agents in simple words"
        }
    ]
)

print(response.choices[0].message.content)