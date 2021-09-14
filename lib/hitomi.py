import json
import requests
import json


def get_info(hitomi_num):
    response = requests.get(
        'https://ltn.hitomi.la/galleries/{}.js'.format(hitomi_num), verify=False)
    # print(response.status_code)
    if response.status_code == 200:
        dict_response = json.loads(response.text.split('=', 1)[1].strip())
        # print(dict_response)
        return {
            'result': 'success',
            'title': dict_response['title'],
            'date': dict_response['date'],
            'language': dict_response['language'],
            'type': dict_response['type'],
            'link': 'https://hitomi.la/galleries/{}.html'.format(dict_response['id'])
        }
    else:
        return {
            'result': 'error',
            'message': '작품이 없는거같습니다 휴-먼'
        }
