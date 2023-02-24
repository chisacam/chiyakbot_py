import functools

from telegram import Message, Update
from telegram.ext import ContextTypes

from .chatbots import AbstractChatbotModel


def privileged_message(method):
    @functools.wraps(method)
    async def decorated(
        self: AbstractChatbotModel,
        update: Update,
        message: Message,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        if message.from_user is None or message.from_user.id != self.owner_id:
            await self.bot.send_message(message.chat.id, "저런! 주인놈이 아니네요!")
            return
        await method(update, message, context)

    return decorated
