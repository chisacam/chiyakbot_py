import sqlite3
from sqlite3.dbapi2 import connect
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
    for title, content in result:
        lines = content.split('.')
        get_line_limit = 5 if len(lines) >= 5 else len(lines)
        summary = ''.join(lines[:get_line_limit])
        results.append(InlineQueryResultArticle(
            id=str(uuid4()),
            title=title,
            input_message_content=InputTextMessageContent(summary),
            description=summary
        ))
    update.inline_query.answer(results)
    sql.close()

def search_namu(query):
    conn = sqlite3.connect('./namu.db')
    sql = conn.cursor()
    sql.execute(f"SELECT summary FROM namu WHERE title='{query}'")
    content = sql.fetchone()
    sql.close()
    result = ''
    if content != None:
        lines = content[0].split('.')
        get_line_limit = 5 if len(lines) >= 5 else len(lines)
        result = ''.join(lines[:get_line_limit])
    else:
        result = '검색결과가 없어요!'
    return result
