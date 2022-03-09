import requests
from bs4 import BeautifulSoup

def getElectionStatus():
    res = requests.get('https://bit.ly/2022-Korean-presidential-election')
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.select_one('#table01')
    the_min_name = table.select_one('tbody > tr:nth-child(1) > td:nth-child(4) > strong').get_text(' ', strip=True)
    gook_gim_name = table.select_one('tbody > tr:nth-child(1) > td:nth-child(5) > strong').get_text(' ', strip=True)
    the_min_per = table.select_one('tbody > tr:nth-child(3) > td:nth-child(4)').get_text()
    gook_gim_per = table.select_one('tbody > tr:nth-child(3) > td:nth-child(5)').get_text()
    print(the_min_name, the_min_per)
    print(gook_gim_name, gook_gim_per)
    return f'{the_min_name} {the_min_per}', f'{gook_gim_name} {gook_gim_per}'

getElectionStatus()