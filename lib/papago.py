import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)


def get_translate(text):
    trans_id = os.getenv('NAVER_TRANS_ID')
    trans_secret = os.getenv('NAVER_TRANS_SECRET')
    detect_id = os.getenv('NAVER_DETECT_ID')
    detect_secret = os.getenv('NAVER_DETECT_SECRET')

    detect_url = 'https://openapi.naver.com/v1/papago/detectLangs'
    trans_url = "https://openapi.naver.com/v1/papago/n2mt"

    trans_header = {
        "X-Naver-Client-Id": trans_id,
        "X-Naver-Client-Secret": trans_secret
    }

    detect_header = {
        "X-Naver-Client-Id": detect_id,
        "X-Naver-Client-Secret": detect_secret
    }

    translated_text = ''

    detect_data = {
        'query': text
    }

    detect_response = requests.post(
        detect_url, headers=detect_header, data=detect_data)
    if(detect_response.status_code != 200):
        translated_text = "Error Code:" + str(detect_response.status_code)
    detect_result = detect_response.json()
    lang = detect_result['langCode']
    trans_data = {
        'text': text,
        'source': lang,
        'target': 'ko'
    }

    trans_response = requests.post(
        trans_url, headers=trans_header, data=trans_data)

    if(trans_response.status_code != 200):
        translated_text = 'Error Code:' + str(trans_response.status_code)

    translated_data = trans_response.json()
    translated_text = translated_data['message']['result']['translatedText']
    return translated_text
