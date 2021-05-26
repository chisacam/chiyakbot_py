import chatbotmodel
import re
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# 유저 chat_id 가져오기


def check_id(update, context):
    try:
        id = update.message.chat.id
        # print(id)
        return id
    except:
        id = update.channel_post.chat.id
        return id

# 유저 닉네임 가져오기


def check_nickname(update, context):
    try:
        nickname = update.message.from_user.first_name
        # print(nickname)
        return nickname
    except:
        nickname = update.channel_post.from_user.first_name
        return nickname

# 도움말 기능


def help_command(update, context):
    id = check_id(update, context)
    chiyak.sendMessage(id, "안녕하세요, " + check_nickname(update,
                       context) + "님. 저는 아래 목록에 있는 일을 할 수 있어요!")
    chiyak.sendMessage(id, "/를 붙여서 사용해야하는 기능들\n\n/about 자기소개\n/pick 구분자(, | . 등등)과 함께 입력하면 하나를 골라주는 기능\n\n=1+1 처럼 =다음에 수식을 쓰면 계산해주는 계산기\n'확률은?'을 뒤에 붙이면 랜덤확률을 말해주는 기능\n'마법의 소라고둥님'으로 시작하면 그래, 아니중 하나로 대답해주는 소라고둥님")

# 자기소개 기능


def about_command(update, context):
    chiyak.sendMessage(check_id(update, context), "저는 다기능 대화형 봇인 치약봇이에요.")

# 정지 기능


def stop_command(update, context):
    if update.message.from_user.id == 46674072:
        chiyak.sendMessage(check_id(update, context), "안녕히주무세요!")
        chiyak.stop()

# 선택장애 치료 기능


def pick_command(update, context):
    is_correct = update.message.text.split(' ', 1)
    if len(is_correct) <= 1:
        update.message.reply_text(
            '구분자(공백, 콤마 등)를 포함해 /pick 뒤에 써주세요!\nex) /pick 1,2,3,4 or /pick 1 2 3 4')
    else:
        text = is_correct[1]
        text = text.strip()
        if ',' in text:
            picklist = text.split(',')
            pick = random.choice(picklist)
            update.message.reply_text(pick)

        elif ' ' in text:
            picklist = text.split(' ')
            pick = random.choice(picklist)
            update.message.reply_text(pick)

# 채팅방 퇴장 기능


def exit_command(update, context):
    if update.message.from_user.id == 46674072:
        update.message.reply_text("안녕히 계세요!")
        chiyak.core.leave_chat(update.message.chat.id)


def delMessage_command(update, context):
    if update.message.from_user.id == 46674072:
        target_id = update.message.reply_to_message.message_id
        target_group = update.message.reply_to_message.chat.id
        chiyak.core.deleteMessage(target_group, target_id)

# 메세지 감지가 필요한 기능들


def messagedetecter(update, context):
    # 채팅창 계산기 기능
    calc_p = re.compile('^=[0-9+\-*/%!^( )]+')
    is_calc = calc_p.match(update.message.text)
    if is_calc:
        result = eval(update.message.text[1:])
        update.message.reply_text(result)

    # 확률대답 기능
    if '확률은?' in update.message.text:
        n = random.randint(0, 100)
        update.message.reply_text("{}퍼센트".format(n))

    # 소라고둥님
    if '마법의 소라고둥님' in update.message.text:
        update.message.reply_text(random.choice(['그래.', '아니.']))


chiyak = chatbotmodel.chiyakbot()
chiyak.add_cmdhandler('help', help_command)
chiyak.add_cmdhandler('about', about_command)
chiyak.add_cmdhandler('stop', stop_command)
chiyak.add_cmdhandler('pick', pick_command)
chiyak.add_cmdhandler('exit', exit_command)
chiyak.add_messagehandler(messagedetecter)
chiyak.add_cmdhandler('del', delMessage_command)
chiyak.start()
