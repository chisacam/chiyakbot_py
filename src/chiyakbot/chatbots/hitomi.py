import json
import textwrap
from typing import Any, List, Mapping

import httpx
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine


class HitomiModel(AbstractChatbotModel):
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [CommandAnswerMachine(self.get_hitomi_info_command, "htm")]

    async def get_info(self, hitomi_num: str) -> Mapping[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://ltn.hitomi.la/galleries/{hitomi_num}.js")
            if resp.status_code == 200:
                dict_response = json.loads(resp.text.split("=", 1)[1].strip())
                # print(dict_response)
                return {
                    "result": "success",
                    "title": dict_response["title"],
                    "date": dict_response["date"],
                    "language": dict_response["language"],
                    "type": dict_response["type"],
                    "link": "https://hitomi.la/galleries/{}.html".format(
                        dict_response["id"]
                    ),
                }
            else:
                return {"result": "error", "message": "작품이 없는거같습니다 휴-먼"}

    async def get_hitomi_info_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        user_input = (message.text or "").split(" ", 1)
        if len(user_input) <= 1:
            await self.bot.send_message(message.chat.id, "번호가 없는거같아요!")
            return
        else:
            result = await self.get_info(user_input[1])
            if result["result"] == "success":
                reply_text = textwrap.dedent(
                    f"""
                    제목: {result["title"]}
                    게시일: {result["date"]}
                    언어: {result["language"]}
                    종류: {result["type"]}

                    바로가기: {result["link"]}

                    만족하시나요 휴-먼?
                """
                )
            else:
                reply_text = result["message"]
            await self.bot.send_message(message.chat.id, reply_text)
