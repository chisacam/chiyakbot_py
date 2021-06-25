import json
import requests
import json


def get_info(hitomi_num):
    response = requests.get(
        'https://ltn.hitomi.la/galleries/{}.js'.format(hitomi_num))
    print(response.text)
    json_response = response.text.split('=', 1)[1]
    print(json_response)
    dict_response = json.loads(json_response.strip())
    print(dict_response['title'])
    return {
        'title': dict_response['title'],
        'date': dict_response['date'],
        'language': dict_response['language'],
        'type': dict_response['type']
    }
