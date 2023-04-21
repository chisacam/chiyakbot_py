
import os
from typing import List

import httpx
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine


class DeeplModel(AbstractChatbotModel):
    name = "Deepl"
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(
                self.deepl_command, "deepl", description="언어감지 후 한국어로 번역"
            )
        ]

    async def get_translate(self, text):
        trans_secret = os.getenv("DEEPL_TRANS_SECRET")
        detect_id = os.getenv("NAVER_DETECT_ID")
        detect_secret = os.getenv("NAVER_DETECT_SECRET")

        assert trans_secret is not None
        assert detect_id is not None
        assert detect_secret is not None

        detect_url = "https://openapi.naver.com/v1/papago/detectLangs"
        trans_url = "https://deepl-translator.p.rapidapi.com/translate"

        trans_header = {
            "content-type": "application/json",
            "X-RapidAPI-Key": trans_secret,
            "X-RapidAPI-Host": "deepl-translator.p.rapidapi.com"
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
            trans_data = {
                "text": text,
                "source": lang,
                "target": "KO"
            }
            translate_response = await client.post(
                trans_url, headers=trans_header, json=trans_data
            )
            if translate_response.status_code != 200:
                return "Error Code:" + str(translate_response.status_code)

            translated_data = translate_response.json()
            translated_text = translated_data["text"]
            return translated_text

    async def deepl_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if message.reply_to_message is not None:
            if message.reply_to_message.text is not None:
                text = message.reply_to_message.text
                cleaned_text = text.replace("\n", " ")
                result = await self.get_translate(cleaned_text)
                await message.reply_text(result)
        else:
            text = (message.text or "").split(" ", 1)
            if len(text) <= 1:
                await message.reply_text(
                    "명령어 뒤에 번역하고자 하는 문장을 쓰거나 답장으로 알려주세요!\n예시: /deepl Heads up that my son's school closed for in-person learning for ten days, starting this afternoon, because of a covid outbreak that began at the end of last week, and all kids and staff who were in that building within the past 48 hours are advised to self-isolate for five days and then get a covid test."
                )
            else:
                cleaned_text = text[1].replace("\n", " ")
                result = await self.get_translate(cleaned_text)
                await message.reply_text(result)
