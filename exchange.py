import requests
from dotenv import load_dotenv
import os
import datetime
import json
from pytz import timezone
import re

load_dotenv(verbose=True)
exchangeJsonPath = './exchange.json'
get_num = re.compile('(\d+)')
get_code = re.compile('([A-Z]+)')

def request_info():
    response = requests.get(
        'https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={}&data=AP01'.format(os.getenv('EXCHANGEKEY')))
    # print(response.status_code)
    if response.status_code == 200:
        dict_response = response.json()
        if dict_response != []:
            if dict_response[0]['result'] == 4:
                return {
                    'result': 'error',
                    'message': '일일 조회한도를 초과했어요! 이전 정보를 드릴게요!'
                }
            data = {}
            for item in dict_response:
                matched_num = get_num.findall(item['cur_unit'])
                matched_code = get_code.findall(item['cur_unit'])
                data[matched_code[0]] = {
                    'code': item['cur_unit'],
                    'name': item['cur_nm'],
                    'unit': 1 if matched_num == [] else matched_num[0],
                    'cur': item['deal_bas_r']
                }
            result = {
                "version": datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y%m%d'),
                "result": "success",
                "message": "요청을 성공했어요!",
                "data": data
            }
            with open(exchangeJsonPath, 'w') as outfile:
                json.dump(result, outfile, indent=4, ensure_ascii=False)
            return result
        else:
            return {
                'result': 'error',
                'message': '해당 요청일의 환율정보가 없어요! 이전 정보를 드릴게요!'
            }
    else:
        return {
            'result': 'error',
            'message': '통신오류 또는 잘못된 요청이래요! 이전 정보를 드릴게요!'
        }


def get_info():
    date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y%m%d')
    data = None
    if os.path.exists(exchangeJsonPath):
        with open(exchangeJsonPath, "r") as json_file:
            data = json.load(json_file)
            if data['version'] != date:
                temp = request_info()
                data = temp if temp['result'] == 'success' else data
    else:
        data = request_info()
    return data
