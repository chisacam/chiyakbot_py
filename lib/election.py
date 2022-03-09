import requests
from bs4 import BeautifulSoup
import datetime, pytz

def getElectionStatus():
    res = requests.get('https://bit.ly/2022-Korean-presidential-election')
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.select_one('#table01')
    the_min_name = table.select_one('tbody > tr:nth-child(1) > td:nth-child(4) > strong').get_text(' ', strip=True).split(' ')[1]
    gook_gim_name = table.select_one('tbody > tr:nth-child(1) > td:nth-child(5) > strong').get_text(' ', strip=True).split(' ')[1]
    the_min_per = table.select_one('tbody > tr:nth-child(3) > td:nth-child(4)').get_text()
    gook_gim_per = table.select_one('tbody > tr:nth-child(3) > td:nth-child(5)').get_text()
    election_per = table.select_one('tbody > tr:nth-child(2) > td:nth-child(19)').get_text()
    base_time = datetime.datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
    diff = float(the_min_per) - float(gook_gim_per)
    diff_per = diff * -1 if diff < 0 else diff
    return f'{the_min_name} {the_min_per}%', f'{gook_gim_name} {gook_gim_per}%', f'{election_per}%', base_time, diff_per
