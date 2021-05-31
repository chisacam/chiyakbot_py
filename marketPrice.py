import requests
import json
import os.path
import datetime
from pytz import timezone
from bs4 import BeautifulSoup
import escape
import chatbotmodel

chiyak = chatbotmodel.chiyakbot()
marketPriceJsonPath = './marketPrice.json'


def checkMarketPrice_command(update, context):
    date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
    data = {}
    want = update.message.text.split(' ')

    if os.path.exists(marketPriceJsonPath):
        with open(marketPriceJsonPath, "r") as json_file:
            data = json.load(json_file)
            if data['version'] != date:
                data = getMarketPrice(date)
    else:
        data = getMarketPrice(date)

    if len(want) <= 1:
        chiyak.sendMessage(update.message.chat_id, '어떤 모델인지 안알려줬거나 형식에 맞지않아요!')
        return
    else:
        price_data = data['data'].items()
        result = {}
        for key, value in price_data:
            if key.startswith(want[1]):
                result[key] = {
                    "modelname": escape.escape_for_marketprice_name_compile.sub('\\\\\\g<0>', value['modelname']),
                    "*price*": "[*{}*]({})".format(value['price'], value['graphLink']),
                }
        if result == {}:
            chiyak.sendMessage(update.message.chat_id,
                               '저런, 검색결과가 없어요! 혹시 마지막글자를 빼면 나오는지 확인해볼게요!')
            for key, value in price_data:
                if key.startswith(want[1][:-1]):
                    result[key] = {
                        "modelname": escape.escape_for_marketprice_name_compile.sub('\\\\\\g<0>', value['modelname']),
                        "*price*": "[*{}*]({})".format(value['price'], value['graphLink']),
                    }
        pretty_result = escape.escape_for_md(json.dumps(
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
