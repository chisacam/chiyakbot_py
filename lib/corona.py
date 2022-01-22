import requests, time

def get_today_info():
    url = f"https://apiv3.corona-live.com/domestic/live.json?timestamp={int(time.time())}"
    response = requests.get(url)
    data = response.json()
    return data