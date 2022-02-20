import requests
import os
from .escape import escape_for_md
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv(verbose=True)
api_key = os.getenv('SAUCENAO_API_KEY')
base_url = f'https://saucenao.com/search.php?db=999&output_type=2&testmode=1&api_key={api_key}&url='

def setSiteName():
    siteName = defaultdict(lambda: 'undefined yet')
    siteNameInitValue = {
        0: 'H-Magazines',
        2: 'H-Game CG',
        3: 'DoujinshiDB',
        5: 'pixiv',
        6: 'pixiv',
        8: 'Nico Nico Seiga',
        9: 'Danbooru',
        10: 'drawr Images',
        11: 'Nijie Images',
        12: 'Yande.re',
        15: 'Shutterstock',
        16: 'FAKKU',
        18: 'H-Misc',
        38: 'H-Misc',
        19: '2D-Market',
        20: 'MediBang',
        21: 'Anime',
        22: 'H-Anime',
        23: 'Movies',
        24: 'Shows',
        25: 'Gelbooru',
        26: 'Konachan',
        27: 'Sankaku Channel',
        28: 'Anime-Pictures.net',
        29: 'e621.net',
        30: 'Idol Complex',
        31: 'bcy.net Illust',
        32: 'bcy.net Cosplay',
        33: 'PortalGraphics.net',
        34: 'deviantArt',
        35: 'Pawoo.net',
        36: 'Madokami (Manga)',
        37: 'MangaDex',
        39: 'ArtStation',
        40: 'FurAffinity',
        41: 'Twitter',
        42: 'Furry Network'
    }
    siteName.update(siteNameInitValue)

    return siteName

def get_similarity(img_info):
    siteName = setSiteName()
    response = requests.get(base_url + img_info.file_path).json()

    sitename = escape_for_md(siteName[response['results'][0]['header']['index_id']], True)

    best_sitelink = response['results'][0]['data']['ext_urls'][0]

    similarity = escape_for_md(
        response['results'][0]['header']['similarity'], True)
    long_remaining = response['header']['long_remaining']

    return sitename, best_sitelink, similarity, long_remaining
