import requests, json

def convert_to_id(target):
    if target == 'cj':
        return 'kr.cjlogistics'
    elif target == '우체국':
        return 'kr.epost'
    elif target == '한진':
        return 'kr.hanjin'
    elif target == '롯데':
        return 'kr.lotte'
    elif target == '로젠':
        return 'kr.logen'
    elif target == 'cu':
        return 'kr.cupost'
    elif target == 'dhl':
        return 'de.dhl'

def get_delivery_info(target, track_id):
    target_id = convert_to_id(target)
    req_url = f"https://apis.tracker.delivery/carriers/{target_id}/tracks/{track_id}"
    req_response = requests.get(req_url)
    data = json.dumps(req_response.json(), ensure_ascii=False, indent=4)
    return json.loads(data)
