import requests, datetime, pytz

def get_today_info():
    time_now = int(datetime.datetime.now(pytz.timezone('Asia/Seoul')).timestamp())
    req_url = f"https://apiv3.corona-live.com/domestic/live.json?timestamp={time_now}"
    last_mod_url = f"https://apiv3.corona-live.com/last-updated.json?timestamp={time_now}"
    req_response = requests.get(req_url)
    last_mod_response = requests.get(last_mod_url)
    data = req_response.json()
    data['last_updated'] = datetime.datetime.fromtimestamp(float(last_mod_response.json()['datetime'] / 1000), pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
    return data