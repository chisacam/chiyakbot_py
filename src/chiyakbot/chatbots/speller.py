import os
import json
from typing import List

import httpx
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine

from .escape import escape_for_md

class SpellerModel(AbstractChatbotModel):
    name = "Speller"
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(
                self.speller_command, "speller", description="맞춤법 검사 by cs.pusan.ac.kr"
            )
        ]
    
    async def generate_message(self, response_json):
        result = ""
        for err in response_json:
            result = f"{result}\n~{err['orgStr']}~ -> {err['candWord']}"
        return escape_for_md(result, True)

    async def request_speller(self, text):
        speller_url = "http://164.125.7.61/speller/results"

        check_target_text = {"text1": text}

        async with httpx.AsyncClient() as client:
            speller_response_raw = await client.post(
                speller_url, data=check_target_text
            )
            if speller_response_raw.status_code != 200:
                return "Error Code:" + str(speller_response_raw.status_code)

            speller_response = speller_response_raw.text.split('data = [', 1)[-1].rsplit('];', 1)[0]
            speller_response_json = json.loads(speller_response)
            return speller_response_json['errInfo']

    async def speller_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if message.reply_to_message is not None:
            if message.reply_to_message.text is not None:
                result = await self.request_speller(message.reply_to_message.text)
                result = await self.generate_message(result)
                await message.reply_text(result, parse_mode="MarkdownV2")
        else:
            text = (message.text or "").split(" ", 1)
            if len(text) <= 1:
                await message.reply_text(
                    "명령어 뒤에 교정하고자 하는 문장을 쓰거나 답장으로 알려주세요!\n예시: /speller 다람쥐 헌 쳇바퀴에 다고파."
                )
            else:
                result = await self.request_speller(text[1])
                result = await self.generate_message(result)
                await message.reply_text(result, parse_mode="MarkdownV2")
