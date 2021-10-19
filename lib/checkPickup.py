import chatbotmodel
import requests
import time
import threading
import json
import os.path
import re
from . import escape

chiyak = chatbotmodel.chiyakbot()
alert_users = {}
file_path = './registerd.json'

if os.path.exists(file_path):
    with open(file_path, "r") as json_file:
        alert_users = json.load(json_file)


def checkPickup_command(update, context):
    is_correct = update.message.text.split(' ')
    length = len(is_correct)
    result = {}
    print(is_correct)
    if length <= 1:
        result = checkPickup()
    else:
        model = is_correct[1].strip()
        result = checkPickup(model)
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
    def __init__(self, name, _type):
        super().__init__()
        self.name = name
        self.type = _type
    def run(self):
        while(True):
            for model in alert_users.keys():
                if checkPickupForLoop(model, self.type):
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
            time.sleep(60)


def checkPickupLoop(update, context):
    if update.message.from_user.id != chiyak.id:
        chiyak.sendMessage(update.message.chat_id, '저런! 주인놈이 아니네요!')
        return
    chiyak.sendMessage(update.message.chat_id, '감시시작!')
    _type = update.message.text.split(' ')
    if len(_type) <= 1:
        t = Worker('cploop', 'pickup')
        t.daemon = True
        t.start()
    else:
        t = Worker('cploop', _type[1])
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


def checkPickup(model='MHR43KH/A'):
    checkPickURL = 'https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}'.format(
        model)
    checkPickableStoreURL = 'https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}&location=06028'.format(
        model)
    
    nameURL = f'https://www.apple.com/kr/shop/configUpdate/{model}'
    univPriceURL = f'https://www.apple.com/kr-k12/shop/configUpdate/{model}'
    baseBuyURL = 'https://www.apple.com/kr/shop/product/'
    baseUnivBuyURL = 'https://www.apple.com/kr-k12/shop/product/'

    r = requests.get(checkPickURL)
    t = requests.get(nameURL)
    u = requests.get(univPriceURL)
    d = r.json()
    n = t.json()
    m = u.json()
    result = {}
    if d['head']['status'] == '200' and 'body' in d and 'body' in n:
        basePickDict = d['body']['content']['pickupMessage']['pickupEligibility'][model]
        baseNameDict = n['body']['replace']['summary']
        baseUnivDict = m['body']['replace']['summary']
        isBuyable = d['body']['content']['deliveryMessage'][model]['isBuyable']
        name = escape.escape_for_md(
            baseNameDict['displayName'], True)
        buyURL = baseBuyURL + model
        univBuyURL = baseUnivBuyURL + model

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
                result['isPickable'] = '씹가능' if available_store != [] else '불가능'
                result['pickableStore'] = available_store if available_store != [
                ] else '재고없음'
            else:
                result['isPickable'] = '불가능'
                result['pickableStore'] = '없음'
            result['isBuyable'] = '씹가능' if isBuyable else '불가능'
            result['price'] = baseNameDict['prices']['total']
            result['univPrice'] = baseUnivDict['prices']['total']
            result['link'] = univBuyURL
            return result
        except Exception as e:
            print(e)
            return '몬가이상함\\(exception\\)'
    else:
        return '팀쿡이 안알랴줌\\(no response body\\)'


def checkPickupForLoop(model, _type):
    checkPickURL = 'https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}'.format(
        model)
    r = requests.get(checkPickURL)
    d = r.json()
    result = d['body']['content']['pickupMessage']['pickupEligibility'][model]['storePickEligible'] if _type == 'pickup' else d['body']['content']['deliveryMessage'][model]['isBuyable']
    return result
