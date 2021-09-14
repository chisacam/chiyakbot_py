import sqlite3
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4

def inlinequeryhandler(update, context):
    query = update.inline_query.query

    if query == "":
        return
    conn = sqlite3.connect('./namu.db')
    sql = conn.cursor()
    sql.execute(f"SELECT * FROM namu WHERE title LIKE '%{query}%' limit 40")
    result = sql.fetchall()
    results = []
    for title, content in result:
        results.append(InlineQueryResultArticle(
            id=str(uuid4()),
            title=title,
            input_message_content=InputTextMessageContent(f'/namu {title}'),
            description=content
        ))
    update.inline_query.answer(results)

def search_namu(query):
    conn = sqlite3.connect('./namu.db')
    sql = conn.cursor()
    sql.execute(f"SELECT summary FROM namu WHERE title LIKE '%{query}%'")
    result = sql.fetchone()
    return result[0]
