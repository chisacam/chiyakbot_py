from typing import List

from inko import Inko
from telegram import Bot, Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine


class InkoModel(AbstractChatbotModel):
    my_inko: Inko
    name = "Inko"
    def __init__(self, bot: Bot, owner_id: str) -> None:
        super().__init__(bot, owner_id)
        self.my_inko = Inko()

    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(
                self.enko_command, "en2ko", description="영타로 쓴 문자열을 한글로 변환"
            ),
            CommandAnswerMachine(
                self.koen_command, "ko2en", description="한글로 쓴 문자열을 영타로 변환"
            ),
        ]

    async def enko_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        if message.reply_to_message is not None:
            await message.reply_text(self.my_inko.en2ko(message.reply_to_message.text))
        else:
            text = (message.text or "").split(" ", 1)
            if len(text) <= 1:
                await message.reply_text(
                    "변환하고자 하는 메세지에 답장을 달거나, 명령어 뒤에 변환하고자 하는 문자열을 써주세요!\n ex)/en2ko dksl"
                )
            else:
                await message.reply_text(self.my_inko.en2ko(text[1]))

    async def koen_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        if message.reply_to_message is not None:
            await message.reply_text(self.my_inko.ko2en(message.reply_to_message.text))
        else:
            text = (message.text or "").split(" ", 1)
            if len(text) <= 1:
                await message.reply_text(
                    "변환하고자 하는 메세지에 답장을 달거나, 명령어 뒤에 변환하고자 하는 문자열을 써주세요!\n ex)/ko2en ㅗ디ㅣㅐ"
                )
            else:
                await message.reply_text(self.my_inko.ko2en(text[1]))
