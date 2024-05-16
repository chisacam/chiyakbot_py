import json
from typing import List

import httpx
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine

class ChzzkModel(AbstractChatbotModel):
    name = "Chzzk m3u8 getter"
    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    default_headers = {
        "User-Agent": UA,
    }
    # 스텔라이브 채널 아이디
    stellive_channel_id = {
        "칸나": "f722959d1b8e651bd56209b343932c01",
        "유니": "45e71a76e949e16a34764deb962f9d9f",
        "리제": "4325b1d5bbc321fad3042306646e2e50",
        "타비": "a6c4ddb09cdb160478996007bff35296",
        "히나": "b044e3a3b9259246bc92e863e7d3f3b8",
        "마시로": "4515b179f86b67b4981e16190817c580",
    }
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(
                self.chzzk_command, "chzzk", description="치지직 m3u8 주소 따기"
            ),
            CommandAnswerMachine(
                self.get_chzzk_stellive_id_command, "chzzk_stellive_id", description="스텔라이브 채널 아이디 확인"
            )
        ]

    async def get_channel_info(self, channel_id: str):
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"https://api.chzzk.naver.com/service/v1/channels/{channel_id}",
                headers=self.default_headers,
            )
            return res.json()

    async def get_live_detail(self, channel_id: str):
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"https://api.chzzk.naver.com/service/v2/channels/{channel_id}/live-detail",
                headers=self.default_headers,
            )
            return res.json()

    async def get_m3u8_path(self, live_detail):
        playback = json.loads(live_detail["content"]["livePlaybackJson"])
        for media in playback["media"]:
            if media["mediaId"] == "HLS":
                return media["path"]
        raise Exception("media not found")
    
    async def make_m3u8_url(self, channel_id):
        live_detail = await self.get_live_detail(channel_id)
        m3u8_path = await self.get_m3u8_path(live_detail)
        return m3u8_path

    async def chzzk_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        text = (message.text or "").split(" ", 1)
        if len(text) <= 1:
            result = await self.make_m3u8_url(self.stellive_channel_id["리제"])
            await message.reply_text(result)
        else:
            result = await self.make_m3u8_url(text[1])
            await message.reply_text(result)
    
    async def get_chzzk_stellive_id_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await message.reply_text(f"스텔라이브 채널 아이디: {json.dump(self.stellive_channel_id, indent=2, ensure_ascii=False)}")
