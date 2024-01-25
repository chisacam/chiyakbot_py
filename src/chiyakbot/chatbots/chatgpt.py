import os
from typing import List
from dotenv import load_dotenv
from openai import AsyncOpenAI
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine

load_dotenv()
aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), organization=os.getenv("OPENAI_ORGANIZATION"))

class ChatGPTModel(AbstractChatbotModel):
    name = "Chat GPT"
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [CommandAnswerMachine(self.handler, "ask")]

    async def handler(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        text = (message.text or "").split(" ", 1)
        if len(text) <= 1:
            await message.reply_text("물어볼 말을 써주세요!")
        else:
            response = await aclient.chat.completions.create(model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "user", "content": text[1]}
                ])
            result = response.choices[0].message.content.strip()
            await message.reply_text(result)
