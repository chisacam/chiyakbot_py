from contextlib import nullcontext
from tabnanny import check
import chatbotmodel
import re
import random
import requests
import time
import threading
import json
import os.path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# 전역변수
calc_p = re.compile('^=[0-9+\-*/%!^( )]+')
ipad_model = re.compile('^M[0-9A-Z]{4}KH/A$')
alert_users = {}
file_path = './registerd.json'

if os.path.exists(file_path):
    with open(file_path, "r") as json_file:
        alert_users = json.load(json_file)

print(alert_users)
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


def checkPickup_command(update, context):
    is_correct = update.message.text.split(' ', 1)
    print(is_correct)
    if len(is_correct) <= 1:
        result = checkPickup()
        res = '''
        이름 : {0}
가격 : {1}
학생가격 : {2}
구매 : {3}
픽업 : {4}
[*학생구매링크*]({5})
        '''.format(result['name'], result['price'], result['univPrice'], result['isBuyable'], result['isPickable'], result['link'])
        update.message.reply_text(res, parse_mode='MarkdownV2')
    else:
        model = is_correct[1].strip()
        if ipad_model.match(model):
            result = checkPickup(model)
            res = '''
            이름 : {0}
가격 : {1}
학생가격 : {2}
구매 : {3}
픽업 : {4}
[*학생구매링크*]({5})
            '''.format(result['name'], result['price'], result['univPrice'], result['isBuyable'], result['isPickable'], result['link'])
            update.message.reply_text(res, parse_mode='MarkdownV2')
        else:
            update.message.reply_text('으엑 퉤퉤퉤')


class Worker(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        while(True):
            for model in alert_users.keys():
                if checkPickupForLoop(model):
                    for chatid in alert_users[model]:
                        result = checkPickup(model)
                        res = '''
                        이름 : {0}
가격 : {1}
학생가격 : {2}
구매 : {3}
픽업 : {4}
[학생구매링크]({5})
                        '''.format(result['name'], result['price'], result['univPrice'], result['isBuyable'], result['isPickable'], result['link'])
                        chiyak.core.sendMessage(
                            chat_id=chatid, text=res, parse_mode='MarkdownV2')
                        chiyak.core.sendMessage(
                            chat_id=chatid, text=res, parse_mode='MarkdownV2')
                        chiyak.core.sendMessage(
                            chat_id=chatid, text=res, parse_mode='MarkdownV2')
                    del alert_users[model][0:]
            time.sleep(300)


def checkPickupLoop(update, context):
    if update.message.from_user.id != 46674072:
        chiyak.sendMessage(update.message.chat_id, '저런! 주인놈이 아니네요!')
        return
    chiyak.sendMessage(update.message.chat_id, '감시시작!')
    t = Worker('cploop')
    t.daemon = True
    t.start()


def checkPickupRegister(update, context):
    is_correct = update.message.text.split(' ', 1)
    print(is_correct, update.message.chat_id)
    if len(is_correct) <= 1:
        if 'MHR43KH/A' not in alert_users:
            alert_users['MHR43KH/A'] = []
        alert_users['MHR43KH/A'].append(update.message.chat_id)
    else:
        key = is_correct[1].strip()
        if key not in alert_users:
            alert_users[key] = []
        alert_users[key].append(update.message.chat_id)
    with open(file_path, 'w') as outfile:
        json.dump(alert_users, outfile, indent=4)
        chiyak.sendMessage(update.message.chat_id, '등록했어요!')


def checkPickupDelete(update, context):
    is_correct = update.message.text.split(' ', 1)
    if len(is_correct) <= 1:
        alert_users['MHR43KH/A'].remove(update.message.chat_id)
    else:
        alert_users[is_correct[1].strip()].remove(update.message.chat_id)
    with open(file_path, 'w') as outfile:
        json.dump(alert_users, outfile, indent=4)
        chiyak.sendMessage(update.message.chat_id, '해제했어요!')


# 메세지 감지가 필요한 기능들

def messagedetecter(update, context):
    try:
        # 채팅창 계산기 기능
        is_calc = calc_p.match(update.message.text)
        if is_calc:
            result = eval(update.message.text[1:])
            update.message.reply_text(result)
        else:
            # 확률대답 기능
            if '확률은?' in update.message.text:
                n = random.randint(0, 100)
                update.message.reply_text("{}퍼센트".format(n))

            # 소라고둥님
            if '마법의 소라고둥님' in update.message.text:
                update.message.reply_text(random.choice(['그래.', '아니.']))
    except Exception as e:
        print(e)


def checkPickup(model='MHR43KH/A'):
    checkPickURL = 'https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}'.format(
        model)
    checkNameURL = 'https://www.apple.com/kr/shop/updateSummary?node=home/shop_ipad/family/ipad_pro&step=select&product={0}'.format(
        model)
    checkUnivPriceURL = 'https://www.apple.com/kr-k12/shop/updateSummary?node=home%2Fshop_ipad%2Ffamily%2Fipad_pro&step=select&product={0}'.format(
        model)
    r = requests.get(checkPickURL)
    t = requests.get(checkNameURL)
    u = requests.get(checkUnivPriceURL)
    d = r.json()
    n = t.json()
    m = u.json()
    result = {}
    if d['head']['status'] == '200' and 'body' in d:
        basePickDict = d['body']['content']['pickupMessage']['pickupEligibility'][model]
        baseNameDict = n['body']['response']['summarySection']
        baseUnivDict = m['body']['response']['summarySection']
        name = re.sub('[.+\\-(),]', '\\\\\\g<0>',
                      baseNameDict['summary']['productTitle'])
        try:
            result['name'] = '[*' + name + \
                '*]({0})'.format(baseNameDict['baseURL'])
            result['isPickable'] = '씹가능' if basePickDict['storePickEligible'] else '불가능'
            result['isBuyable'] = '씹가능' if baseNameDict['summary']['isBuyable'] else '불가능'
            result['price'] = format(
                round(int(baseNameDict['summary']['seoPrice'].split('.')[0]), 0), ",")
            result['univPrice'] = format(
                round(int(baseUnivDict['summary']['seoPrice'].split('.')[0]), 0), ",")
            result['link'] = baseNameDict['baseURL'].replace('kr', 'kr-k12')
            return result
        except Exception as e:
            print(e)
            return '몬가이상함(exception)'
    else:
        return '팀쿡이 안알랴줌(no response body)'


def checkPickupForLoop(model):
    checkPickURL = 'https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}'.format(
        model)
    r = requests.get(checkPickURL)
    d = r.json()
    return d['body']['content']['pickupMessage']['pickupEligibility'][model]['storePickEligible']


chiyak = chatbotmodel.chiyakbot()
chiyak.add_cmdhandler('cp', checkPickup_command)
chiyak.add_cmdhandler('cpl', checkPickupLoop)
chiyak.add_cmdhandler('cpr', checkPickupRegister)
chiyak.add_cmdhandler('cpd', checkPickupDelete)
chiyak.add_cmdhandler('help', help_command)
chiyak.add_cmdhandler('about', about_command)
chiyak.add_cmdhandler('stop', stop_command)
chiyak.add_cmdhandler('pick', pick_command)
chiyak.add_cmdhandler('exit', exit_command)
chiyak.add_cmdhandler('del', delMessage_command)
chiyak.add_messagehandler(messagedetecter)

chiyak.start()
