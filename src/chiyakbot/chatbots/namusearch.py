from typing import List
from uuid import uuid4

import aiosqlite
from telegram import (InlineQueryResult, InlineQueryResultArticle,
                      InputTextMessageContent, Update)
from telegram.ext import ContextTypes

from . import AbstractChatbotModel, BaseAnswerMachine, InlineQueryAnswerMachine


class NamuSearchModel(AbstractChatbotModel):
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [InlineQueryAnswerMachine(self.handler)]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.inline_query is None:
            return
        query = update.inline_query.query
        if query == "":
            return

        results: List[InlineQueryResult] = []

        async with aiosqlite.connect("./namu.db") as conn:
            async with conn.execute(
                f"SELECT * FROM namu WHERE title LIKE '{query}%' limit 50"
            ) as cursor:
                async for title, content in cursor:
                    lines = content.split(".")
                    get_line_limit = 5 if len(lines) >= 5 else len(lines)
                    summary = ".".join(lines[:get_line_limit])
                    results.append(
                        InlineQueryResultArticle(
                            id=str(uuid4()),
                            title=title,
                            input_message_content=InputTextMessageContent(summary),
                            description=summary,
                        )
                    )
        await update.inline_query.answer(results)
