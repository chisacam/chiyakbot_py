from datetime import datetime
import io
import os
from typing import Any, List, Mapping

import httpx
import prettytable
from PIL import Image, ImageDraw, ImageFont
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine

all_code = ["USD","CNY","JPY","EUR","HKD","TWD","VND","CAD","RUB","THB","PHP","SGD","AUD","GBP","MYR","ZAR","NOK","NZD","DKK","MXN","MNT","BHD","BDT","BRL","BND","SAR","LKR","SEK","CHF","AED","DZD","OMR","JOD","ILS","EGP","INR","IDR","CZK","CLP","KZT","QAR","KES","COP","KWD","TZS","TRY","PKP","PLN","HUF"]
top_code = ["USD","CNY","JPY(100)","EUR","HKD","TWD","GBP","VND","CAD","RUB"]


class ExchangeModel(AbstractChatbotModel):
    name = "Exchange"
    api_key = os.getenv("EXCHANGE_API_KEY")
    async def request_info(self, req_code="USD") -> Mapping[str, Any]:
        match req_code:
            case "ALL":
                req = all_code
            case "TOP":
                req = top_code
            case _:
                req = req_code

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={self.api_key}&data=AP01"
            )
            # print(response.status_code)
            if response.status_code == 200:
                dict_response = response.json()
                if dict_response != []:
                    return {
                        "result": True,
                        "message": "요청을 성공했어요!",
                        "data": dict_response,
                    }
                else:
                    return {
                        "result": False,
                        "message": "통신오류 또는 결과값이 없어요! 입력값을 다시 확인해보세요!",
                    }
            else:
                return {
                    "result": False,
                    "message": "통신오류 또는 잘못된 요청이래요! 입력값을 다시 확인해보세요!",
                }

    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(
                self.get_exchange_command, "exch", description="현재 환율표"
            ),
            CommandAnswerMachine(
                self.calc_exchange_command, "exchc", description="현재 환율 기반으로 원화 변환"
            ),
        ]

    def get_target_exchange_data(self, exchange_data, target_code):
        target_data = []
        for item in exchange_data:
            if item["cur_unit"].replace("(100)", "") in target_code:
                item["cur_unit"] = item["cur_unit"].replace("(100)", "")
                target_data.append(item)
        return target_data

    async def get_exchange_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        result = ""
        input_code = "USD"
        user_input = (message.text or "").split(" ", 1)
        table = prettytable.PrettyTable(["CODE", "BASE", "BUY", "SELL"])
        table.align["CODE"] = "l"
        table.align["BASE"] = "r"
        table.align["BUY"] = "r"
        table.align["SELL"] = "r"
        if len(user_input) > 1:
            input_code = user_input[1].upper()
        exchange_data = await self.request_info()
        target_data = []
        if exchange_data["result"]:
            now = datetime.now()
            target_data = self.get_target_exchange_data(exchange_data["data"], input_code)
            result += "date: " + now.date().strftime("%Y%m%d") + "\n"
            result += "time: " + now.timetz().strftime("%H:%M:%S") + "\n"
            for item in target_data:
                # print(item)
                table.add_row(
                    [
                        item["cur_unit"],
                        item["deal_bas_r"],
                        item["ttb"],
                        item["tts"],
                    ]
                )
            result += table.get_string()
        else:
            message = exchange_data["message"]
            await message.reply_text(f"{message}")
        im = Image.new("RGB", (250, 110 + len(target_data) * 19), "white")
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("./JetBrainsMonoNL-Regular.ttf", 13)
        draw.text((10, 10), result, font=font, fill="black")
        im_byte = io.BytesIO()
        im.save(im_byte, format="png", bitmap_format="png")
        await self.bot.send_photo(message.chat.id, im_byte.getvalue())
        im.close()
        im_byte.close()

    async def calc_exchange_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        result = None
        user_input = (message.text or "").split(" ")
        if len(user_input) <= 2:
            await message.reply_text("뭔가 빠진거같아요! 다시 시도해주세요!")
        else:
            input_code = user_input[1].upper()
            exchange_data = await self.request_info()
            input_cur = round(float(user_input[2].replace(",", "")), 2)
            format_cur = format(input_cur, ",")
            if exchange_data["result"]:
                try:
                    item = self.get_target_exchange_data(exchange_data["data"], input_code)[0]
                    result = format(
                        round(
                            float(item["deal_bas_r"].replace(",", ""))
                            * input_cur
                            / (100 if item["cur_unit"] == "JPY" else 1),
                            2,
                        ),
                        ",",
                    )
                    await message.reply_text(
                        f"{format_cur} {input_code} ≈ {result} KRW"
                    )
                except:
                    await message.reply_text(
                        "계산중에 오류가 발생했어요! 지원하지 않는 통화코드거나 값을 잘못 쓰신거같아요! 다시 시도해보세요."
                    )
                    return
            else:
                message = exchange_data["message"]
                await message.reply_text(f"{message}")
