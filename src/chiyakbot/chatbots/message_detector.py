import asyncio
import random
import re
from typing import Final, List

from telegram import Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, MessageAnswerMachine

calc_p = re.compile("^=[0-9+\-*/%!^( )]+")

NEUTRAL_STICKER: Final[
    str
] = "CAACAgUAAxkBAAEUGcBig96Z7Obt7mu7albA4-zCFQsnvQACUAUAAsRjUVfojFwLEBPkxSQE"
ONE_MORE_NEUTRAL_STICKER: Final[
    str
] = "CAACAgUAAxkBAAEUKWBihi70wSv8O0LB_wp460MurNq7-gACOwQAAjloUVfvJCcbD0Mk4iQE"
POSITIVE_STICKER: Final[
    str
] = "CAACAgUAAxkBAAEUKcpihkF6RHdtOS24z9DMc2qF4ZjHPQAC8gQAAjqYyFfcus59q-EwJiQE"
NEGATIVE_STICKER: Final[
    str
] = "CAACAgUAAxkBAAEUKcxihkF8uQewGgABK5awbAhQ1qnqnIsAAtIDAAJrUMlXERp-qMX1H_UkBA"
INDETERMINATE_STICKER: Final[
    str
] = "CAACAgUAAxkBAAEUKWhihjGtpLDaatZuCzXcWQ8-IXxiWgACrQUAAtc9yFc1WwupLBD6niQE"


class MessageDetectorModel(AbstractChatbotModel):
    name = "Message Detector"
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [MessageAnswerMachine(self.detect_message, description="확률 계산기")]

    async def detect_message(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        text = message.text
        if text is None:
            return
        try:
            # 채팅창 계산기 기능
            is_calc = calc_p.match(text)
            if is_calc:
                result = round(float(eval(text[1:])), 2)
                await message.reply_text(str(result))
            else:
                # 확률대답 기능
                if "확률은?" in text:
                    n = random.randint(0, 100)
                    await message.reply_text(f"{n}퍼센트")

                # 소라고둥님
                if "마법의 소라고둥님" in text:
                    # message.reply(random.choice(['그래.', '아니.']))
                    await message.reply_sticker(NEUTRAL_STICKER)
                    await asyncio.sleep(2)
                    if random.choices([True, False], weights=[0.2, 0.8])[0]:
                        await message.reply_sticker(ONE_MORE_NEUTRAL_STICKER)
                        await asyncio.sleep(2)
                    await message.reply_sticker(
                        random.choices(
                            [POSITIVE_STICKER, NEGATIVE_STICKER, INDETERMINATE_STICKER],
                            weights=[0.45, 0.45, 0.1],
                        )[0]
                    )
        except Exception as e:
            print(e)
