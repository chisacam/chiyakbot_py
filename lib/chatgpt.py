import openai
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

openai.api_key = os.getenv('CHAT_GPT_SECRET_KEY')

def ask_chatbot(question='지금 몇시야?'):
    response = openai.Completion.create(
        prompt=question, 
        engine="text-davinci-003",
        max_tokens=2048,
        temperature=0.3, 
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()