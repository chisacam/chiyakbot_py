import os
from typing import List

import httpx
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine


class PapagoModel(AbstractChatbotModel):
    name = "Papago"
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(
                self.papago_command, "papago", description="언어감지 후 한국어로 번역"
            )
        ]

    async def get_translate(self, text):
        trans_id = os.getenv("NAVER_TRANS_ID")
        trans_secret = os.getenv("NAVER_TRANS_SECRET")
        detect_id = os.getenv("NAVER_DETECT_ID")
        detect_secret = os.getenv("NAVER_DETECT_SECRET")

        assert trans_id is not None
        assert trans_secret is not None
        assert detect_id is not None
        assert detect_secret is not None

        detect_url = "https://openapi.naver.com/v1/papago/detectLangs"
        trans_url = "https://openapi.naver.com/v1/papago/n2mt"

        trans_header = {
            "X-Naver-Client-Id": trans_id,
            "X-Naver-Client-Secret": trans_secret,
        }

        detect_header = {
            "X-Naver-Client-Id": detect_id,
            "X-Naver-Client-Secret": detect_secret,
        }

        translated_text = ""

        detect_data = {"query": text}

        async with httpx.AsyncClient() as client:
            detect_response = await client.post(
                detect_url, headers=detect_header, data=detect_data
            )
            if detect_response.status_code != 200:
                return "Error Code:" + str(detect_response.status_code)

            detect_result = detect_response.json()
            lang = detect_result["langCode"]
            trans_data = {"text": text, "source": lang, "target": "ko"}
            translate_response = await client.post(
                trans_url, headers=trans_header, data=trans_data
            )
            if translate_response.status_code != 200:
                return "Error Code:" + str(translate_response.status_code)

            translated_data = translate_response.json()
            translated_text = translated_data["message"]["result"]["translatedText"]
            return translated_text

    async def papago_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if message.reply_to_message is not None:
            if message.reply_to_message.text is not None:
                result = await self.get_translate(message.reply_to_message.text)
                await message.reply_text(result)
        else:
            text = (message.text or "").split(" ", 1)
            if len(text) <= 1:
                await message.reply_text(
                    "명령어 뒤에 번역하고자 하는 문장을 쓰거나 답장으로 알려주세요!\n예시: /papago Heads up that my son's school closed for in-person learning for ten days, starting this afternoon, because of a covid outbreak that began at the end of last week, and all kids and staff who were in that building within the past 48 hours are advised to self-isolate for five days and then get a covid test."
                )
            else:
                cleaned_text = text[1].replace("\n", " ")
                result = await self.get_translate(cleaned_text)
                await message.reply_text(result)
