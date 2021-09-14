import sqlite3
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4

def inlinequeryhandler(update, context):
    query = update.inline_query.query

    if query == "":
        return
    conn = sqlite3.connect('./namu.db')
    sql = conn.cursor()
    sql.execute(f"SELECT * FROM namu WHERE title LIKE '{query}%' limit 50")
    result = sql.fetchall()
    results = []
    i = 0
    for title, content in result:
        results.append(InlineQueryResultArticle(
            id=str(i),
            title=title,
            input_message_content=InputTextMessageContent(f'/namu {title}'),
            description=content
        ))
        i += 1
    update.inline_query.answer(results)
    sql.close()

def search_namu(query):
    conn = sqlite3.connect('./namu.db')
    sql = conn.cursor()
    sql.execute(f"SELECT summary FROM namu WHERE title LIKE '%{query}%'")
    result = sql.fetchone()
    sql.close()
    return result[0] if result != None else '검색결과가 없어요!'
