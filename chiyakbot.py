from contextlib import nullcontext
from queue import Empty
from tabnanny import check
import chatbotmodel
import re
import random
import requests
import time
import threading
import json
import os.path
import datetime
from pytz import timezone
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# 전역변수
calc_p = re.compile('^=[0-9+\-*/%!^( )]+')
ipad_model = re.compile('^M[0-9A-Z]{4}KH/A$')
escape_for_md_compile = re.compile('[.+\\-(),}{/:=&]')
escape_for_marketprice_compile = re.compile('[.+\\-,}{/:=&]')
escape_for_marketprice_name_compile = re.compile('[)(]')
alert_users = {}
file_path = './registerd.json'
marketPriceJsonPath = './marketPrice.json'

available_modeltype = ['ipad_pro', 'ipad_air',
                       'ipad_mini', 'ipad_10_2', 'iphone_12',
                       'iphone_12_pro', 'iphone_se', 'iphone_xr',
                       'iphone_11']
helpText = """/를 붙여서 사용해야하는 기능들

/about 자기소개
/pick 구분자(, | . 등등)과 함께 입력하면 하나를 골라주는 기능

/cp [modelcode?] [modeltype?] 모델코드 입력하면 애플스토어 구매/픽업 가능여부 알려주는 기능
modelcode가 없으면 기본값은 5세대 12.9 128 셀룰러 스페이스그레이 모델
modeltype이 없으면 기본값은 ipad_pro, 가능한 모델타입은 아래와 같음
{0}

/cpr [modelcode] 모델코드 입력하면 애플스토어 픽업 가능할때 해당 채팅방에 알려주는 기능
modelcode가 없으면 기본값은 5세대 12.9 128 셀룰러 스페이스그레이 모델

/cpd [modelcode] 모델코드 입력하면 픽업 감시 취소
modelcode가 없으면 5세대 12.9 128 셀룰러 스페이스 그레이 예약한것 취소

'='다음에 수식을 쓰면 계산해주는 계산기
ex) =1+1 or =2*2

'확률은?'을 뒤에 붙이면 랜덤확률을 말해주는 기능
ex) 오늘 일론머스크가 또 헛소리할 확률은?

'마법의 소라고둥님'으로 시작하면 그래, 아니중 하나로 대답해주는 소라고둥님
ex) 마법의 소라고둥님 오늘 도지가 화성에 갈까요?
""".format(available_modeltype)

if os.path.exists(file_path):
    with open(file_path, "r") as json_file:
        alert_users = json.load(json_file)

print(alert_users)
# 유저 chat_id 가져오기


def escape_for_md(text, isPickup):
    result = ''
    if isPickup:
        result = escape_for_md_compile.sub('\\\\\\g<0>', text)
    else:
        result = escape_for_marketprice_compile.sub('\\\\\\g<0>', text)
    return result


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
    chiyak.sendMessage(id, helpText)

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
    is_correct = update.message.text.split(' ')
    length = len(is_correct)
    result = {}
    print(is_correct)
    if length <= 1:
        result = checkPickup()
    else:
        model = is_correct[1].strip()
        if ipad_model.match(model) and length == 2:
            result = checkPickup(model)
        elif ipad_model.match(model) and length == 3:
            prodType = is_correct[2].strip()
            result = checkPickup(model, prodType)
        else:
            update.message.reply_text('으엑 퉤퉤퉤')
            return
    if type(result) is str:
        update.message.reply_text(result, parse_mode='MarkdownV2')
    else:
        res = '''
        이름 : {0}
가격 : {1}
학생가격 : {2}
구매 : {3}
픽업 : {4}
픽업가능스토어 : {5}
[*학생구매링크*]({6})
        '''.format(result['name'], result['price'], result['univPrice'], result['isBuyable'], result['isPickable'], result['pickableStore'], result['link'])
        update.message.reply_text(res, parse_mode='MarkdownV2')


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
                        if type(result) is str:
                            continue
                        res = '''
                        이름 : {0}
가격 : {1}
학생가격 : {2}
구매 : {3}
픽업 : {4}
픽업가능스토어 : {5}
[*학생구매링크*]({6})
                        '''.format(result['name'], result['price'], result['univPrice'], result['isBuyable'], result['isPickable'], result['pickableStore'], result['link'])
                        chiyak.core.sendMessage(
                            chat_id=chatid, text=res, parse_mode='MarkdownV2')
                        chiyak.core.sendMessage(
                            chat_id=chatid, text=res, parse_mode='MarkdownV2')
                        chiyak.core.sendMessage(
                            chat_id=chatid, text=res, parse_mode='MarkdownV2')
                    del alert_users[model][0:]
            with open(file_path, 'w') as outfile:
                emptylist = list(alert_users.keys())
                for model in emptylist:
                    if len(alert_users[model]) == 0:
                        del alert_users[model]
                json.dump(alert_users, outfile, indent=4)
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
        if 'MHR43KH/A' not in alert_users:
            chiyak.sendMessage(update.message.chat_id, '예약하신 적이 없어요!')
            return
        alert_users['MHR43KH/A'].remove(update.message.chat_id)
        if len(alert_users['MHR43KH/A']) == 0:
            del alert_users['MHR43KH/A']
    else:
        model = is_correct[1].strip()
        if model not in alert_users:
            chiyak.sendMessage(update.message.chat_id, '예약하신 적이 없어요!')
            return
        alert_users[model].remove(update.message.chat_id)
        if len(alert_users[model]) == 0:
            del alert_users[model]
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


def checkPickup(model='MHR43KH/A', prodType='ipad_pro'):
    checkPickURL = 'https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}'.format(
        model)
    checkPickableStoreURL = 'https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}&location=06028'.format(
        model)
    checkIpadNameURL = 'https://www.apple.com/kr/shop/updateSummary?node=home/shop_ipad/family/{0}&step=select&product={1}'.format(
        prodType, model)
    checkIphoneNameURL = 'https://www.apple.com/kr/shop/updateSummary?node=home/shop_iphone/family/{0}&step=select&igt=true&product={1}'.format(
        prodType, model)
    checkUnivPriceURL = 'https://www.apple.com/kr-k12/shop/updateSummary?node=home%2Fshop_ipad%2Ffamily%2F{0}&step=select&product={1}'.format(
        prodType if 'ipad' in prodType else 'ipad_pro', model)
    baseBuyURL = 'https://www.apple.com/kr/shop/product/'
    baseUnivBuyURL = 'https://www.apple.com/kr-k12/shop/product/'

    r = requests.get(checkPickURL)
    t = requests.get(checkIpadNameURL if
                     'ipad' in prodType else checkIphoneNameURL)
    u = requests.get(checkUnivPriceURL)
    d = r.json()
    n = t.json()
    m = u.json()
    result = {}
    if d['head']['status'] == '200' and 'body' in d and 'body' in n:
        basePickDict = d['body']['content']['pickupMessage']['pickupEligibility'][model]
        baseNameDict = n['body']['response']['summarySection']
        baseUnivDict = m['body']['response']['summarySection']
        name = escape_for_md(baseNameDict['summary']['productTitle'], True)
        buyURL = baseNameDict['baseURL'] if 'baseURL' in baseNameDict else baseBuyURL + model
        univBuyURL = baseNameDict['baseURL'].replace(
            'kr', 'kr-k12') if 'baseURL' in baseNameDict else baseUnivBuyURL + model

        try:
            result['name'] = '[*' + name + \
                '*]({0})'.format(buyURL)
            if basePickDict['storePickEligible']:
                store = requests.get(checkPickableStoreURL).json()[
                    'body']['content']['pickupMessage']['stores']
                available_store = []
                if store[0]['partsAvailability'][model]['storeSelectionEnabled']:
                    available_store.append('가로수길')
                if store[1]['partsAvailability'][model]['storeSelectionEnabled']:
                    available_store.append('여의도')
                result['isPickable'] = '씹가능'
                result['pickableStore'] = available_store
            else:
                result['isPickable'] = '불가능'
                result['pickableStore'] = '없음'
            result['isBuyable'] = '씹가능' if baseNameDict['summary']['isBuyable'] else '불가능'
            result['price'] = format(
                round(int(baseNameDict['summary']['seoPrice'].split('.')[0]), 0), ",")
            result['univPrice'] = format(
                round(int(baseUnivDict['summary']['seoPrice'].split('.')[0]), 0), ",")
            result['link'] = univBuyURL
            return result
        except Exception as e:
            print(e)
            return '몬가이상함\\(exception\\)'
    else:
        return '팀쿡이 안알랴줌\\(no response body\\)'


def checkPickupForLoop(model):
    checkPickURL = 'https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}'.format(
        model)
    r = requests.get(checkPickURL)
    d = r.json()
    return d['body']['content']['pickupMessage']['pickupEligibility'][model]['storePickEligible']


def checkMarketPrice_command(update, context):
    date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
    data = {}
    if os.path.exists(marketPriceJsonPath):
        with open(marketPriceJsonPath, "r") as json_file:
            data = json.load(json_file)
            if data['version'] != date:
                data = getMarketPrice(date)
    else:
        data = getMarketPrice(date)
    want = update.message.text.split(' ')
    if len(want) <= 1:
        chiyak.sendMessage(update.message.chat_id, '어떤 모델인지 안알려줬거나 형식에 맞지않아요!')
        return
    else:
        price_data = data['data'].items()
        result = {}
        for key, value in price_data:
            if key.startswith(want[1]):
                result[key] = {
                    "modelname": escape_for_marketprice_name_compile.sub('\\\\\\g<0>', value['modelname']),
                    "*price*": "[*{}*]({})".format(value['price'], value['graphLink']),
                }
        if result == {}:
            chiyak.sendMessage(update.message.chat_id,
                               '저런, 검색결과가 없어요! 혹시 마지막글자를 빼면 나오는지 확인해볼게요!')
            for key, value in price_data:
                if key.startswith(want[1][:-1]):
                    result[key] = {
                        "modelname": escape_for_marketprice_name_compile.sub('\\\\\\g<0>', value['modelname']),
                        "*price*": "[*{}*]({})".format(value['price'], value['graphLink']),
                    }
        pretty_result = escape_for_md(json.dumps(
            result, ensure_ascii=False, indent=4), False)
        chiyak.core.sendMessage(
            chat_id=update.message.chat_id, text=pretty_result, parse_mode='MarkdownV2')


def getMarketPrice(today):
    result = {
        "version": today,
        "data": {}
    }
    checkPriceURL = 'https://price.cetizen.com'
    r = requests.get(checkPriceURL)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.select('#make_0 > div > div > ul')
    for item in table:
        infos = item.select('li > a')
        if len(infos) < 3:
            continue
        result['data'][infos[1].get_text().strip()] = {
            "modelname": infos[0].get_text().strip(),
            "price": infos[2].get_text().strip(),
            "graphLink": infos[0].get('href')
        }
    with open(marketPriceJsonPath, 'w') as outfile:
        json.dump(result, outfile, indent=4, ensure_ascii=False)
    return result


chiyak = chatbotmodel.chiyakbot()
chiyak.add_cmdhandler('cmp', checkMarketPrice_command)
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
