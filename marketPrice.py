import requests
import json
import os.path
import datetime
from pytz import timezone
from bs4 import BeautifulSoup
import escape

marketPriceJsonPath = './marketPrice.json'


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


def get_select_model_price(want):
    date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
    data = {}

    if os.path.exists(marketPriceJsonPath):
        with open(marketPriceJsonPath, "r") as json_file:
            data = json.load(json_file)
            if data['version'] != date:
                data = getMarketPrice(date)
    else:
        data = getMarketPrice(date)

    price_data = data['data'].items()
    result = {}
    for key, value in price_data:
        if key.startswith(want):
            result[key] = {
                "modelname": escape.escape_for_marketprice_name_compile.sub('\\\\\\g<0>', value['modelname']),
                "*price*": "[*{}*]({})".format(value['price'], value['graphLink']),
            }
    if result == {}:
        for key, value in price_data:
            if key.startswith(want[:-1]):
                result[key] = {
                    "modelname": escape.escape_for_marketprice_name_compile.sub('\\\\\\g<0>', value['modelname']),
                    "*price*": "[*{}*]({})".format(value['price'], value['graphLink']),
                }
    return escape.escape_for_md(json.dumps(
        result, ensure_ascii=False, indent=4), False)
