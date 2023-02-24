import os
from typing import List

import openai
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine

openai.api_key = os.getenv("CHAT_GPT_SECRET_KEY")


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
            response = await openai.Completion.acreate(
                prompt=text[1],
                engine="text-davinci-003",
                max_tokens=2048,
                temperature=0.3,
                top_p=1.0,
                frequency_penalty=0,
                presence_penalty=0,
            )
            result = response.choices[0].text.strip()
            await message.reply_text(result)
