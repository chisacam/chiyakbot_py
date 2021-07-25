import requests
from bs4 import BeautifulSoup
from cairosvg import svg2png

def get_kospnamu():
    response = requests.get("https://playboard.co/channel/UCMC9OdBCMVIGMtVSYvQsYag")
    bs = BeautifulSoup(response.text, 'html.parser')
    rank = bs.select_one('#app > div.__window > div > div > main > article > div > div > div > div > div > section.widget.rt-ranking.widget.subs-ranking > div.widget__body > div.rank > div.rank__current')
    rank_status = bs.select_one('#app > div.__window > div > div > main > article > div > div > div > div > div > section.widget.rt-ranking.widget.subs-ranking > div.widget__body > div.rank > div.rank__fluc.down > span')
    # print(rank, rank_status)
    return rank.get_text().strip(), rank_status.get_text().strip()