import json
from typing import List

import httpx
from telegram import Message, Update
from telegram.ext import ContextTypes

from .regex import is_uuid, escape_for_md

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine

class ChzzkModel(AbstractChatbotModel):
    name = "Chzzk m3u8 getter"
    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    default_headers = {
        "User-Agent": UA,
    }
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(
                self.chzzk_command, "chzzk", description="치지직 m3u8 주소 따기"
            ),
        ]

    async def search_channel(self, keyword: str):
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "https://api.chzzk.naver.com/service/v1/search/channels",
                params={
                    "keyword": keyword,
                    "offset": 0,
                    "size": 5,
                    "withFirstChannelContent": "true",
                },
                headers=self.default_headers,
            )
            resJson = res.json()
            return resJson["content"]["data"]

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
            live = res.json()
            return live["content"]

    def get_m3u8_path(self, live_detail):
        playback = json.loads(live_detail["livePlaybackJson"])
        for media in playback["media"]:
            if media["mediaId"] == "HLS":
                return media["path"]
        return ""

    def get_title(self, live_detail):
        return live_detail["liveTitle"]
    
    def parse_channel_live_detail(self, search_result):
        details = []
        for data in search_result:
            if data["channel"]["openLive"] == True and "content" in data:
                details.append(data["content"]["live"])
        return details
    
    def make_m3u8_url(self, live_detail):
        title = self.get_title(live_detail)
        m3u8_path = self.get_m3u8_path(live_detail)
        if m3u8_path == "":
            return "저런, 방송중이 아닌것같아요!"
        return f"{title}\n\n{m3u8_path}"

    async def chzzk_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        text = (message.text or "").split(" ", 1)
        if len(text) <= 1:
            await message.reply_text("명령어 뒤에 채널명이나 채널id를 써주세요!")
        else:
            if is_uuid.match(text[1]):
                live_detail = await self.get_live_detail(text[1])
                result = self.make_m3u8_url(live_detail)
                await message.reply_text(result)
            else:
                search_result = await self.search_channel(text[1])
                details = self.parse_channel_live_detail(search_result)
                if len(details) == 0:
                    await message.reply_text("저런, 방송중이 아닌거같아요!")
                else:
                    result = []
                    for detail in details:
                        result.append(self.make_m3u8_url(detail))
                    await message.reply_text("\n".join(result))

