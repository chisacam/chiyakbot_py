import time
import datetime
from pytz import timezone
import threading
import json
import os.path
import re
import chatbotmodel
import uuid
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

chiyak = chatbotmodel.chiyakbot()
file_path = './reminded.json'
alert_users = []
is_only_time = re.compile(
    '^((202[0-9]{1})(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01]))?((0[0-9]|1[0-9]|2[0-3])([0-5][0-9])){1}$')
DREMIND = 0
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
                now = datetime.datetime.now(
                    timezone('Asia/Seoul')).strftime('%Y%m%d%H%M')
                if now >= remind_task['remind_date']:
                    chiyak.core.sendMessage(chat_id=remind_task['remind_chat_id'], reply_to_message_id=remind_task['remind_message_id'], text='다시 확인해보실 시간이에요!\n메모: {}'.format(
                        remind_task['remind_text']))
                    alert_users.remove(remind_task)
            with open(file_path, 'w') as outfile:
                json.dump(alert_users, outfile, indent=4, ensure_ascii=False)
            time.sleep(60)


def start_remind_loop(update, context):
    if update.message.from_user.id != chiyak.id:
        chiyak.sendMessage(update.message.chat_id, '저런! 주인놈이 아니네요!')
        return
    chiyak.sendMessage(update.message.chat_id, '리마인드 스레드 시작!')
    t = Worker('remdloop')
    t.daemon = True
    t.start()


def reminder_register(update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    remind_text_id = update.message.message_id
    user_input = update.message.text.split(' ', 2)
    if update.message.reply_to_message is not None:
        if update.message.reply_to_message.text is not None:
            if len(user_input) > 1:
                result = regist(chat_id, user_id, update.message.reply_to_message.text,
                                remind_text_id, user_input[1].strip(), 'reply')
                update.message.reply_text(result['message'])
            else:
                update.message.reply_text(
                    '언제 다시 알려드릴지 모르겠어요. 입력을 다시 확인해주세요!\n/remind [날짜] [리마인드할문자열]\n또는\n리마인드할 메세지에 답장후 /remind [날짜]')
                return
        else:
            update.message.reply_text('텍스트를 찾을 수 없어요!')
            return
    else:
        if len(user_input) > 2:
            result = regist(chat_id, user_id, user_input[2].strip(
            ), remind_text_id, user_input[1].strip(), 'param')
            update.message.reply_text(result['message'])
        else:
            update.message.reply_text(
                '다시 알려드릴 시간이나 메세지를 못찾겠어요. 입력을 다시 확인해주세요!\n/remind [날짜] [리마인드할문자열]\n또는\n리마인드할 메세지에 답장후 /remind [날짜]')
            return
    with open(file_path, 'w') as outfile:
        json.dump(alert_users, outfile, indent=4, ensure_ascii=False)


def reminder_delete_command(update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    registered_work = [[KeyboardButton(text='{}\n\n{}'.format(item['remind_text'], item['remind_uuid']))]
                       for item in alert_users if item['reminder_user_id'] == user_id]
    if len(registered_work) == 0:
        chiyak.core.sendMessage(chat_id=chat_id, text='삭제할 리마인더가 없어요!')
        return ConversationHandler.END
    registered_work.append([KeyboardButton(text='선택종료')])
    update.message.reply_text('취소할 리마인더를 선택해주세요!', reply_markup=ReplyKeyboardMarkup(
        keyboard=registered_work, resize_keyboard=True, selective=True))
    return DREMIND


def remind_delete_error(update, context):
    #    with open(file_path, 'w') as outfile:
    #        json.dump(alert_users, outfile, indent=4, ensure_ascii=False)
    #        chiyak.sendMessage(update.message.chat_id, '해제했어요!')
    update.message.reply_text(
        '에러 또는 선생님의 선택으로 취소됐어요!', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def remind_delete(update, context):
    token = update.message.text.split('\n')
    if token[0] == '선택종료':
        update.message.reply_text(
            '리마인더 선택 끝! 삭제할게요!', reply_markup=ReplyKeyboardRemove()
        )
        with open(file_path, 'w') as outfile:
            json.dump(alert_users, outfile, indent=4, ensure_ascii=False)
            update.message.reply_text('삭제처리 끝!')
            return ConversationHandler.END
    else:
        for remind_task in alert_users[:]:
            if token[2] == remind_task['remind_uuid']:
                chiyak.core.sendMessage(chat_id=remind_task['remind_chat_id'], text='리마인더 {}를 선택했어요!'.format(
                    remind_task['remind_text']))
                alert_users.remove(remind_task)
        return DREMIND


def regist(chat_id, user_id, remind_text, remind_text_id, user_date, type):
    result = is_correct_time(user_date)

    if result['result']:
        alert_users.append({
            'remind_date': result['date'],
            'remind_chat_id': chat_id,
            'remind_input_type': type,
            'reminder_user_id': user_id,
            'remind_message_id': remind_text_id,
            'remind_text': remind_text,
            'remind_uuid': str(uuid.uuid4())
        })
        alert_users.sort(key=lambda alert_user: alert_user['remind_text'])

    return result


def is_correct_time(user_date):
    default_date = datetime.datetime.now(
        timezone('Asia/Seoul')).strftime('%Y%m%d')
    is_correct = {}
    fin_date = default_date + user_date if len(user_date) == 4 else user_date
    if is_only_time.match(user_date):
        is_correct['result'] = True
        is_correct['date'] = fin_date
        is_correct['message'] = '{}에 다시 알려드릴게요!'.format(
            datetime.datetime.strptime(fin_date, "%Y%m%d%H%M"))
    else:
        is_correct['result'] = False
        is_correct['message'] = '저런, 날짜형식에 맞지 않는것같아요! 아래 예시를 참고해주세요!\nYYYYmmddHHMM(예시: 202107071800)\n또는\nHHMM(예시: 1800)'

    return is_correct


rm_remind_handler = ConversationHandler(
    entry_points=[CommandHandler('dremind', reminder_delete_command)],
    states={
        DREMIND: [MessageHandler(Filters.text, remind_delete)]
    },
    fallbacks=[CommandHandler('drcancel', remind_delete_error)],
)
