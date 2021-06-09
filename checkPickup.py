import chatbotmodel
import requests
import time
import threading
import json
import os.path
import re
import escape

chiyak = chatbotmodel.chiyakbot()
alert_users = {}
file_path = './registerd.json'
ipad_model = re.compile('^M[0-9A-Z]{4}KH/A$')

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
            time.sleep(180)


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
        name = escape.escape_for_md(
            baseNameDict['summary']['productTitle'], True)
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
                result['isPickable'] = '씹가능' if available_store != [] else '불가능'
                result['pickableStore'] = available_store if available_store != [
                ] else '재고없음'
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
