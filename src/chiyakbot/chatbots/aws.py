import os
from typing import List, Tuple

from aiobotocore.session import AioSession
from telegram import Bot, Message, Update
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine


class AWSModel(AbstractChatbotModel):
    sess: AioSession
    name = "Detect Sentiment"

    def __init__(self, bot: Bot, owner_id: str) -> None:
        super().__init__(bot, owner_id)
        self.comprehend = AioSession()

    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(
                self.sentiment_handler,
                "ds",
                description="답장을 사용한 메세지의 긍정/부정에 따라 괜찮아요/나빠요 출력",
            )
        ]

    async def detect_sentiment(self, text: str) -> Tuple[float, float]:
        async with self.sess.create_client(
            service_name="comprehend",
            region_name="ap-northeast-2",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        ) as client:
            result = await client.detect_sentiment(Text=text, languageCode="ko")
            return (
                result["SentimentScore"]["Positive"],
                result["SentimentScore"]["Negative"],
            )

    async def sentiment_handler(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if message.reply_to_message is not None:
            if message.reply_to_message.text is not None:
                pos, neg = await self.detect_sentiment(message.reply_to_message.text)
                await self.bot.send_message(
                    message.chat.id,
                    "나빠요" if pos < neg else "괜찮아요",
                    reply_to_message_id=message.reply_to_message.message_id,
                )
            else:
                await message.reply_text("텍스트에만 사용 해주세요!")
        else:
            user_input = (message.text or "").split(" ", 1)
            if len(user_input) <= 1:
                await message.reply_text("원하는 텍스트에 답장을 걸고 사용하거나, 명령어 뒤에 원하는 문자열을 써주세요!")
                return
            else:
                pos, neg = await self.detect_sentiment(user_input[1])
                await message.reply_text("나빠요" if pos < neg else "괜찮아요")
