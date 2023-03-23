import io
from typing import Any, List, Mapping

import httpx
import prettytable
from PIL import Image, ImageDraw, ImageFont
from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine

all_code = "FRX.KRWUSD,FRX.KRWCNY,FRX.KRWJPY,FRX.KRWEUR,FRX.KRWHKD,FRX.KRWTWD,FRX.KRWVND,FRX.KRWCAD,FRX.KRWRUB,FRX.KRWTHB,FRX.KRWPHP,FRX.KRWSGD,FRX.KRWAUD,FRX.KRWGBP,FRX.KRWMYR,FRX.KRWZAR,FRX.KRWNOK,FRX.KRWNZD,FRX.KRWDKK,FRX.KRWMXN,FRX.KRWMNT,FRX.KRWBHD,FRX.KRWBDT,FRX.KRWBRL,FRX.KRWBND,FRX.KRWSAR,FRX.KRWLKR,FRX.KRWSEK,FRX.KRWCHF,FRX.KRWAED,FRX.KRWDZD,FRX.KRWOMR,FRX.KRWJOD,FRX.KRWILS,FRX.KRWEGP,FRX.KRWINR,FRX.KRWIDR,FRX.KRWCZK,FRX.KRWCLP,FRX.KRWKZT,FRX.KRWQAR,FRX.KRWKES,FRX.KRWCOP,FRX.KRWKWD,FRX.KRWTZS,FRX.KRWTRY,FRX.KRWPKP,FRX.KRWPLN,FRX.KRWHUF"
top_code = "FRX.KRWUSD,FRX.KRWCNY,FRX.KRWJPY,FRX.KRWEUR,FRX.KRWHKD,FRX.KRWTWD,FRX.KRWGBP,FRX.KRWVND,FRX.KRWCAD,FRX.KRWRUB"
base_code = "FRX.KRW"


class ExchangeModel(AbstractChatbotModel):
    name = "Exchange"
    async def request_info(self, req_code="TOP") -> Mapping[str, Any]:
        match req_code:
            case "ALL":
                req = all_code
            case "TOP":
                req = top_code
            case _:
                req = base_code + req_code

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes={req}"
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

    async def get_exchange_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        result = ""
        input_code = "TOP"
        user_input = (message.text or "").split(" ", 1)
        table = prettytable.PrettyTable(["CODE", "BASE", "BUY", "SELL"])
        table.align["CODE"] = "l"
        table.align["BASE"] = "r"
        table.align["BUY"] = "r"
        table.align["SELL"] = "r"
        if len(user_input) > 1:
            input_code = user_input[1].upper()
        exchange_data = await self.request_info(input_code)
        if exchange_data["result"]:
            result += "date: " + exchange_data["data"][0]["date"] + "\n"
            result += "time: " + exchange_data["data"][0]["time"] + "\n"
            for item in exchange_data["data"]:
                # print(item)
                table.add_row(
                    [
                        item["currencyCode"],
                        round(item["basePrice"]),
                        round(item["cashBuyingPrice"]),
                        round(item["cashSellingPrice"]),
                    ]
                )
            result += table.get_string()
        else:
            message = exchange_data["message"]
            await message.reply_text(f"{message}")
        im = Image.new("RGB", (280, len(exchange_data["data"]) * 30), "white")
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("DejaVuSansMono.ttf", 15)
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
            exchange_data = await self.request_info(input_code)
            input_cur = round(float(user_input[2].replace(",", "")), 2)
            format_cur = format(input_cur, ",")
            if exchange_data["result"]:
                try:
                    item = exchange_data["data"][0]
                    result = format(
                        round(
                            float(item["basePrice"])
                            * input_cur
                            / int(item["currencyUnit"]),
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
