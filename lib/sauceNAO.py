import requests
from .escape import escape_for_md

base_url = 'https://saucenao.com/search.php?db=999&output_type=2&testmode=1&api_key=e0bd2877c4c8fb636e2d49143ac1d02408229ca7&url='


def getSiteName(index_id):
    if index_id == 0:
        return 'H-Magazines'

    elif index_id == 2:
        return 'H-Game CG'

    elif index_id == 3:
        return 'DoujinshiDB'

    elif index_id == 5 or index_id == 6:
        return 'pixiv'

    elif index_id == 8:
        return 'Nico Nico Seiga'

    elif index_id == 9:
        return 'Danbooru'

    elif index_id == 10:
        return 'drawr Images'

    elif index_id == 11:
        return 'Nijie Images'

    elif index_id == 12:
        return 'Yande.re'

    elif index_id == 15:
        return 'Shutterstock'

    elif index_id == 16:
        return 'FAKKU'

    elif index_id == 18 or index_id == 38:
        return 'H-Misc'

    elif index_id == 19:
        return '2D-Market'

    elif index_id == 20:
        return 'MediBang'

    elif index_id == 21:
        return 'Anime'

    elif index_id == 22:
        return 'H-Anime'

    elif index_id == 23:
        return 'Movies'

    elif index_id == 24:
        return 'Shows'

    elif index_id == 25:
        return 'Gelbooru'

    elif index_id == 26:
        return 'Konachan'

    elif index_id == 27:
        return 'Sankaku Channel'

    elif index_id == 28:
        return 'Anime-Pictures.net'

    elif index_id == 29:
        return 'e621.net'

    elif index_id == 30:
        return 'Idol Complex'

    elif index_id == 31:
        return 'bcy.net Illust'

    elif index_id == 32:
        return 'bcy.net Cosplay'

    elif index_id == 33:
        return 'PortalGraphics.net'

    elif index_id == 34:
        return 'deviantArt'

    elif index_id == 35:
        return 'Pawoo.net'

    elif index_id == 36:
        return 'Madokami (Manga)'

    elif index_id == 37:
        return 'MangaDex'

    elif index_id == 39:
        return 'ArtStation'

    elif index_id == 40:
        return 'FurAffinity'

    elif index_id == 41:
        return 'Twitter'

    elif index_id == 42:
        return 'Furry Network'

    else:
        return 'undefined yet'


def get_similarity(img_info):
    print(img_info)
    response = requests.get(base_url + img_info.file_path).json()

    sitename = escape_for_md(getSiteName(
        response['results'][0]['header']['index_id']), True)

    best_sitelink = response['results'][0]['data']['ext_urls'][0]

    similarity = escape_for_md(
        response['results'][0]['header']['similarity'], True)
    long_remaining = response['header']['long_remaining']

    return sitename, best_sitelink, similarity, long_remaining
