import os
import load_dotenv

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set - please head to the troubleshooting guide in the setup folder")

env = os.getenv

from dotenv import dotenv_values
for k, v in dotenv_values('.env').items():
    print(f'{k}={v}')


