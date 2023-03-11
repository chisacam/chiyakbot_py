import os
import textwrap
from typing import List, Tuple

import httpx
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine
from .escape import escape_for_md

api_key = os.getenv("SAUCENAO_API_KEY")
base_url = f"https://saucenao.com/search.php?db=999&output_type=2&testmode=1&api_key={api_key}&url="
sites = {
    0: "H-Magazines",
    2: "H-Game CG",
    3: "DoujinshiDB",
    5: "pixiv",
    6: "pixiv",
    8: "Nico Nico Seiga",
    9: "Danbooru",
    10: "drawr Images",
    11: "Nijie Images",
    12: "Yande.re",
    15: "Shutterstock",
    16: "FAKKU",
    18: "H-Misc",
    38: "H-Misc",
    19: "2D-Market",
    20: "MediBang",
    21: "Anime",
    22: "H-Anime",
    23: "Movies",
    24: "Shows",
    25: "Gelbooru",
    26: "Konachan",
    27: "Sankaku Channel",
    28: "Anime-Pictures.net",
    29: "e621.net",
    30: "Idol Complex",
    31: "bcy.net Illust",
    32: "bcy.net Cosplay",
    33: "PortalGraphics.net",
    34: "deviantArt",
    35: "Pawoo.net",
    36: "Madokami (Manga)",
    37: "MangaDex",
    39: "ArtStation",
    40: "FurAffinity",
    41: "Twitter",
    42: "Furry Network",
}


class SimilarImageModel(AbstractChatbotModel):
    name = "sauceNAO"
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(
                self.simimg_command, "simimg", description="답장을 사용한 메세지의 사진 출처를 찾아주는 기능"
            )
        ]

    async def get_similarity(self, img_info) -> Tuple[str, str, str, str]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(base_url + img_info.file_path)
            data = resp.json()

        sitename = escape_for_md(
            sites.get(data["results"][0]["header"]["index_id"], "undefined yet"), True
        )
        best_sitelink = data["results"][0]["data"]["ext_urls"][0]
        similarity = escape_for_md(data["results"][0]["header"]["similarity"], True)
        long_remaining = data["header"]["long_remaining"]

        return sitename, best_sitelink, similarity, long_remaining

    async def simimg_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if (
            message.reply_to_message is not None
            and message.reply_to_message.photo != []
        ):
            img_info = await self.bot.get_file(
                message.reply_to_message.photo[-1].file_id
            )
            (
                sitename,
                best_sitelink,
                similarity,
                long_remaining,
            ) = await self.get_similarity(img_info)
            await message.reply_text(
                textwrap.dedent(
                    f"""
                [*{sitename}*]({best_sitelink}) 에서 가장 비슷한 이미지를 발견했어요\\!
                유사도: *{similarity}*
                남은 일일 검색횟수: *{long_remaining}*
            """
                ),
                parse_mode="MarkdownV2",
            )
        else:
            await message.reply_text("사진이 없는거같아요! 사진에 답장을 써주세요!")
