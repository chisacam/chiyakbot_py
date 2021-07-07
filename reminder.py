import time
import datetime
from pytz import timezone
import threading
import json
import os.path
import re
import chatbotmodel
import telegram
import escape

chiyak = chatbotmodel.chiyakbot()
file_path = './reminded.json'
alert_users = []
is_only_time = re.compile('^[0-9]{4}$')
if os.path.exists(file_path):
    with open(file_path, "r") as json_file:
        alert_users = json.load(json_file)


class Worker(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        while(True):
            for remind_task in alert_users[:]:
                now = datetime.datetime.now().strftime('%Y%m%d%H%M')
                print(now, remind_task['remind_date'])
                if now >= remind_task['remind_date']:
                    chiyak.core.sendMessage(chat_id=remind_task['remind_chat_id'], reply_to_message_id=remind_task['remind_message_id'], text='[{}](tg://user?id={})님\\, 다시 확인해보실 시간이에요\\!\\\n메모\\: {}'.format(
                        remind_task['reminder_user_name'], remind_task['reminder_user_id'], remind_task['remind_text']), parse_mode='MarkdownV2')
                    alert_users.remove(remind_task)
            with open(file_path, 'w') as outfile:
                json.dump(alert_users, outfile, indent=4, ensure_ascii=False)
            time.sleep(60)


def start_remind_loop(update, context):
    if update.message.from_user.id != 46674072:
        chiyak.sendMessage(update.message.chat_id, '저런! 주인놈이 아니네요!')
        return
    chiyak.sendMessage(update.message.chat_id, '리마인드 스레드 시작!')
    t = Worker('remdloop')
    t.daemon = True
    t.start()


def reminder_register(update, context):
    print(update.message)
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username
    chat_id = update.message.chat_id
    default_date = datetime.datetime.now(
        timezone('Asia/Seoul')).strftime('%Y%m%d')
    print(user_id, default_date)
    if update.message.reply_to_message is not None:
        if update.message.reply_to_message.text is not None:
            user_input = update.message.text.split(' ', 1)
            if len(user_input) > 1:
                remind_text = update.message.reply_to_message.text
                remind_text_id = update.message.reply_to_message.message_id
                user_date = user_input[1].strip()
                print(user_date)
                fin_date = default_date + \
                    user_date if is_only_time.match(user_date) else user_date
                print(fin_date)
                alert_users.append({
                    'remind_date': fin_date,
                    'remind_chat_id': chat_id,
                    'remind_input_type': 'reply',
                    'reminder_user_id': user_id,
                    'remind_message_id': remind_text_id,
                    'remind_text': escape.escape_for_md(remind_text, True),
                    'reminder_user_name': escape.escape_for_md(user_name, True)
                })
                alert_users.sort(
                    key=lambda alert_user: alert_user['remind_text'])
                update.message.reply_text('{}에 다시 알려드릴게요!'.format(
                    datetime.datetime.strptime(fin_date, "%Y%m%d%H%M")))
            else:
                update.message.reply_text('언제 다시 알려드릴지 모르겠어요. 입력을 다시 확인해주세요!')
                return
        else:
            update.message.reply_text('텍스트를 찾을 수 없어요!')
    else:
        user_input = update.message.text.split(' ', 2)
        if len(user_input) > 2:
            remind_text = user_input[2].strip()
            remind_text_id = update.message.message_id
            user_date = user_input[1].strip()
            print(user_date)
            fin_date = default_date + \
                user_date if is_only_time.match(user_date) else user_date
            print(fin_date)
            alert_users.append({
                'remind_date': fin_date,
                'remind_chat_id': chat_id,
                'remind_input_type': 'param',
                'reminder_user_id': user_id,
                'remind_message_id': remind_text_id,
                'remind_text': escape.escape_for_md(remind_text, True),
                'reminder_user_name': escape.escape_for_md(user_name, True)
            })
            alert_users.sort(key=lambda alert_user: alert_user['remind_text'])
            update.message.reply_text('{}에 다시 알려드릴게요!'.format(
                datetime.datetime.strptime(fin_date, "%Y%m%d%H%M")))
        else:
            update.message.reply_text('다시 알려드릴 시간이나 메모를 못찾겠어요. 입력을 다시 확인해주세요!')
            return
    with open(file_path, 'w') as outfile:
        json.dump(alert_users, outfile, indent=4, ensure_ascii=False)


def reminder_delete(update, context):
    user_id = update.message.from_user.id
    registered_work = []
    for text in alert_users[user_id]:
        registered_work.append(text['remind_text'])
    telegram.ReplyKeyboardMarkup(keyboard=registered_work)
    with open(file_path, 'w') as outfile:
        json.dump(alert_users, outfile, indent=4, ensure_ascii=False)
        chiyak.sendMessage(update.message.chat_id, '해제했어요!')
