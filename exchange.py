import requests
import json
import datetime
from pytz import timezone

all_code = 'FRX.KRWUSD,FRX.KRWCNY,FRX.KRWJPY,FRX.KRWEUR,FRX.KRWHKD,FRX.KRWTWD,FRX.KRWVND,FRX.KRWCAD,FRX.KRWRUB,FRX.KRWTHB,FRX.KRWPHP,FRX.KRWSGD,FRX.KRWAUD,FRX.KRWGBP,FRX.KRWMYR,FRX.KRWZAR,FRX.KRWNOK,FRX.KRWNZD,FRX.KRWDKK,FRX.KRWMXN,FRX.KRWMNT,FRX.KRWBHD,FRX.KRWBDT,FRX.KRWBRL,FRX.KRWBND,FRX.KRWSAR,FRX.KRWLKR,FRX.KRWSEK,FRX.KRWCHF,FRX.KRWAED,FRX.KRWDZD,FRX.KRWOMR,FRX.KRWJOD,FRX.KRWILS,FRX.KRWEGP,FRX.KRWINR,FRX.KRWIDR,FRX.KRWCZK,FRX.KRWCLP,FRX.KRWKZT,FRX.KRWQAR,FRX.KRWKES,FRX.KRWCOP,FRX.KRWKWD,FRX.KRWTZS,FRX.KRWTRY,FRX.KRWPKP,FRX.KRWPLN,FRX.KRWHUF'
top_code = 'FRX.KRWUSD,FRX.KRWCNY,FRX.KRWJPY,FRX.KRWEUR,FRX.KRWHKD,FRX.KRWTWD,FRX.KRWGBP,FRX.KRWVND,FRX.KRWCAD,FRX.KRWRUB'
base_code= 'FRX.KRW'

def request_info(req_code='TOP'):
    req = ''
    if req_code == 'ALL':
        req = all_code
    elif req_code == 'TOP':
        req = top_code
    else:
        req = base_code + req_code
    response = requests.get(
        'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes={}'.format(req))
    # print(response.status_code)
    if response.status_code == 200:
        dict_response = response.json()
        if dict_response != []:
            return {
                'result': True,
                'message': '요청을 성공했어요!',
                'data': dict_response
            }
        else:
            return {
            'result': False,
            'message': '통신오류 또는 결과값이 없어요! 입력값을 다시 확인해보세요!'
        }
    else:
        return {
            'result': False,
            'message': '통신오류 또는 잘못된 요청이래요! 입력값을 다시 확인해보세요!'
        }