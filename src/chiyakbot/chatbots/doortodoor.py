import textwrap
from typing import Any, List, Mapping

import httpx
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine

name_id_mapping = {
    "cj": "kr.cjlogistics",
    "우체국": "kr.epost",
    "한진": "kr.hanjin",
    "롯데": "kr.lotte",
    "로젠": "kr.logen",
    "cu": "kr.cupost",
    "dhl": "de.dhl",
}


class DeliveryInfoModel(AbstractChatbotModel):
    name = "Delivery Info"

    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [CommandAnswerMachine(self.handler, "dtd", description="택배조회")]

    async def get_delivery_info(self, target: str, track_id: str) -> Mapping[str, Any]:
        target_id = name_id_mapping.get(target)
        req_url = (
            f"https://apis.tracker.delivery/carriers/{target_id}/tracks/{track_id}"
        )
        async with httpx.AsyncClient() as client:
            resp = await client.get(req_url)
            return resp.json()

    async def handler(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        text = (message.text or "").split(" ")
        if len(text) <= 1:
            await message.reply_text(
                "조회 대상과 번호를 모두 입력해주세요!\n사용가능 택배사: cj, 한진, 우체국, 롯데, 로젠, cu, dhl"
            )
        else:
            result = await self.get_delivery_info(text[1], text[2])
            progress_text = ""
            for progress in result["progresses"]:
                progress_text += f"{progress['location']['name']} {progress['status']['text']} {(progress['time'])}\n\n"
            reply_text = textwrap.dedent(
                f"""
                발송인: {result['from']['name']}
                수신인: {result['to']['name']}
                상태: {result['state']['text']}

                현황

                {progress_text}
            """
            )
            await message.reply_text(reply_text)
