import chatbotmodel, requests, time, re, random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bs4 import BeautifulSoup
from selenium import webdriver

menu = []
tags = []
avnumlist_tag = []
avnumlist_name = []
avnamecheck = re.compile('^[a-zA-Z]+[-][0-9]+')
yn = ['그래.', '아니.']
calc_p = re.compile('^=[0-9+[-]*/%!^( )]+')

#유저 chat_id 가져오기
def check_id(bot, update):
    try:
        id = update.message.chat.id
        #print(id)
        return id
    except:
        id = update.channel_post.chat.id
        return id

#유저 닉네임 가져오기
def check_nickname(bot, update):
    try:
        nickname = update.message.from_user.first_name
        #print(nickname)
        return nickname
    except:
        nickname = update.channel_post.from_user.first_name
        return nickname

#도움말 기능
def help_command(bot, update):
    id = check_id(bot, update)
    nick = check_nickname(bot, update)
    chiyak.sendMessage(id,"안녕하세요, " + nick + "님. 저는 아래 목록에 있는 일을 할 수 있어요!")
    chiyak.sendMessage(id, "/를 붙여서 사용해야하는 기능들\n\n/about 자기소개\n/update 창원대 기숙사식단표 업데이트\n/dogfood 창원대 기숙사식단표 보여주기\n/pick 구분자(, | . 등등)과 함께 입력하면 하나를 골라주는 기능\n/tagrank avsee 태그랭킹 보여주기\n/avsearch 태그나 배우이름으로 품번 가져오기\n/getav 품번을 입력하면 영상링크 가져오기\n\n기타기능\n\n=1+1 처럼 =다음에 수식을 쓰면 계산해주는 계산기\n'확률은?'을 뒤에 붙이면 랜덤확률을 말해주는 기능\n'마법의 소라고둥님'으로 시작하면 그래, 아니중 하나로 대답해주는 소라고둥님")

#자기소개 기능
def about_command(bot, update):
    id = check_id(bot, update)
    chiyak.sendMessage(id,"저는 다기능 대화형 봇인 치약봇이에요.")

#정지 기능
def stop_command(bot, update):
    id = check_id(bot, update)
    chiyak.sendMessage(id,"안녕히주무세요!")
    chiyak.stop()

#식단표 데이터 업데이트 기능
def dogfood_update(bot, update):
    id = check_id(bot, update)
    chiyak.sendMessage(id, "식단 데이터를 업데이트 하는 중이에요!")
    
    req = requests.get('http://portal.changwon.ac.kr/homePost/list.do?homecd=dorm&bno=2382')
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    #foodurl_list = soup.find_all("td", {"class":"aline_left"})
    #foodurl = foodurl_list[0].find('a')
    tr = soup.select('body > div#mirae_board > form > div.board_wrap > div.post_body > table > tbody > tr')[0]
    tableurl = tr.find('a').get('href')
    Main_URL = 'http://portal.changwon.ac.kr/homePost/' + tableurl
    
    reqtb = requests.get(Main_URL)
    tablehtml = reqtb.text
    tbsoup = BeautifulSoup(tablehtml, 'html.parser')
    table = tbsoup.select('body > div#mirae_board > form > input')
    global menu
    del menu[:]
    menu.append(table[3].get('value'))
    menu.append(table[4].get('value'))
    menu.append(table[5].get('value'))
    menu.append(table[6].get('value'))
    menu.append(table[7].get('value'))
    menu.append(table[8].get('value'))
    menu.append(table[9].get('value'))    
    menu.append(table[10].get('value'))
    menu[0] = menu[0].replace('|', '~')

    chiyak.sendMessage(id, "업데이트가 완료 되었어요!")

#채팅창 식단표 gui메뉴 빌더
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

#메뉴에 달릴 버튼 빌더
def build_button(text_list) : # make button list
    button_list = []

    for text in text_list :
        button_list.append(InlineKeyboardButton(text, callback_data=text))

    return button_list

#식단기능
def dogfood_command(bot, update):
    button_list = build_button(["월", "화", "수", "목", "금", "토", "일", "그만보기"]) # make button list
    show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1)) # make markup
    update.message.reply_text("현재 식단표는 " + menu[0] + " 기간의 식단표에요!")
    update.message.reply_text("원하는 요일을 선택해주세요!", reply_markup=show_markup) # reply text with markup

#메뉴 버튼 콜백함수
def dogfood_callback(bot, update):
    data_selected = update.callback_query.data
    if data_selected.find("그만보기") != -1:
        chiyak.core.edit_message_text(text="안녕히 가세요!", chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id)
        return

    elif data_selected.find("월") != -1:
        dogmenu = menu[1].split('||')
        dogmenu[4] = dogmenu[4].replace('|', '')
        button_list = build_button(["월", "화", "수", "목", "금", "토", "일", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text="[아침]\n" + dogmenu[0] + "\n[점심A]\n" + dogmenu[1] + "\n[점심B]\n" + dogmenu[2] + "\n[저녁]\n" + dogmenu[4], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)    

    elif data_selected.find("화") != -1:
        dogmenu = menu[2].split('||')
        dogmenu[4] = dogmenu[4].replace('|', '')
        button_list = build_button(["월", "화", "수", "목", "금", "토", "일", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text="[아침]\n" + dogmenu[0] + "\n[점심A]\n" + dogmenu[1] + "\n[점심B]\n" + dogmenu[2] + "\n[저녁]\n" + dogmenu[4], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)    

    elif data_selected.find("수") != -1:
        dogmenu = menu[3].split('||')
        dogmenu[4] = dogmenu[4].replace('|', '')
        button_list = build_button(["월", "화", "수", "목", "금", "토", "일", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text="[아침]\n" + dogmenu[0] + "\n[점심A]\n" + dogmenu[1] + "\n[점심B]\n" + dogmenu[2] + "\n[저녁]\n" + dogmenu[4], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)    

    elif data_selected.find("목") != -1:
        dogmenu = menu[4].split('||')
        dogmenu[4] = dogmenu[4].replace('|', '')
        button_list = build_button(["월", "화", "수", "목", "금", "토", "일", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text="[아침]\n" + dogmenu[0] + "\n[점심A]\n" + dogmenu[1] + "\n[점심B]\n" + dogmenu[2] + "\n[저녁]\n" + dogmenu[4], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)   

    elif data_selected.find("금") != -1:
        dogmenu = menu[5].split('||')
        dogmenu[4] = dogmenu[4].replace('|', '')
        button_list = build_button(["월", "화", "수", "목", "금", "토", "일", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text="[아침]\n" + dogmenu[0] + "\n[점심A]\n" + dogmenu[1] + "\n[점심B]\n" + dogmenu[2] + "\n[저녁]\n" + dogmenu[4], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)    

    elif data_selected.find("토") != -1:
        dogmenu = menu[6].split('||')
        dogmenu[4] = dogmenu[4].replace('|', '')
        button_list = build_button(["월", "화", "수", "목", "금", "토", "일", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text="[아침]\n" + dogmenu[0] + "\n[점심A]\n" + dogmenu[1] + "\n[점심B]\n" + dogmenu[2] + "\n[저녁]\n" + dogmenu[4], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find("일") != -1:
        dogmenu = menu[7].split('||')
        dogmenu[4] = dogmenu[4].replace('|', '')
        button_list = build_button(["월", "화", "수", "목", "금", "토", "일", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text="[아침]\n" + dogmenu[0] + "\n[점심A]\n" + dogmenu[1] + "\n[점심B]\n" + dogmenu[2] + "\n[저녁]\n" + dogmenu[4], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('1') != -1:
        button_list = build_button(["1", "2", "3", "4", "5", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=tags[0], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('2') != -1:
        button_list = build_button(["1", "2", "3", "4", "5", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=tags[1], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('3') != -1:
        button_list = build_button(["1", "2", "3", "4", "5", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=tags[2], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('4') != -1:
        button_list = build_button(["1", "2", "3", "4", "5", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=tags[3], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('5') != -1:
        button_list = build_button(["1", "2", "3", "4", "5", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=tags[4], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('첫번째') != -1:
        button_list = build_button(["첫번째", "두번째", "세번째", "네번째", "다섯번째", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=avnumlist_tag[0], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('두번째') != -1:
        button_list = build_button(["첫번째", "두번째", "세번째", "네번째", "다섯번째", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=avnumlist_tag[1], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('세번째') != -1:
        button_list = build_button(["첫번째", "두번째", "세번째", "네번째", "다섯번째", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=avnumlist_tag[2], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('네번째') != -1:
        button_list = build_button(["첫번째", "두번째", "세번째", "네번째", "다섯번째", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=avnumlist_tag[3], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

    elif data_selected.find('다섯번째') != -1:
        button_list = build_button(["첫번째", "두번째", "세번째", "네번째", "다섯번째", "그만보기"])
        show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
        chiyak.core.edit_message_text(text=avnumlist_tag[4], chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, reply_markup=show_markup)

#AVSEE 태그 랭킹 데이터 업데이트
def tag_update(bot, update):
    req_popular_tag = requests.get('https://avsee04.tv/bbs/tag.php?sort=popular')
    html_p = req_popular_tag.text
    soup_p = BeautifulSoup(html_p, 'html.parser')
    tag_list = soup_p.select('body > div#thema_wrapper > div.wrapper > div#content_wrapper > div.content > div.at-content > div#at-wrap > div#at-main > div.row > div.col-sm-3.col-xs-6 > div.ellipsis > a')
    global tags
    del tags[:]
    text = ""
    count = 0
    for tag in tag_list:
        text = text + "\n" + tag.text.strip()
        count += 1
        if count % 20 == 0:
            tags.append(text)
            text = ""
    

#AVSEE 태그 랭킹 보여주는 기능
def rank_tag_command(bot, update):
    tag_update(bot, update)
    button_list = build_button(["1", "2", "3", "4", "5", "그만보기"])
    show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
    update.message.reply_text("각 페이지당 상위 20개씩의 태그를 보여줘요!")
    update.message.reply_text("원하는 페이지를 선택해주세요!", reply_markup=show_markup)

#AVSEE 영상 품번 검색 기능
def av_search_command(bot, update):
    if update.message.text in '/avsearch':
        update.message.reply_text('검색할 태그를 뒤에 써주세요! 최소 2글자 이상이여야 하고, 반드시 한개의 태그만 검색 해야해요!\n가능예시)/avsearch #여대생 or /avsearch 아스카 키라라\n불가능예시)/avsearch #여대생 #거유 or /avsearch #아스카 키라라')
    else:
        tag = update.message.text[10:]
        tag = tag.strip()
        tag = tag.replace('#', '%23')
        tag = tag.replace(' ', '+')
        req_search_tag = requests.get('https://avsee04.tv/bbs/tag.php?stx=' + tag)
        html_tag = req_search_tag.text
        soup_tag = BeautifulSoup(html_tag, 'html.parser')
        is_empty = soup_tag.select('body > div#thema_wrapper > div.wrapper > div#content_wrapper > div.content > div.at-content > div#at-wrap > div#at-main > div.tagbox-media > p')
        base_url = 'https://avsee04.tv/bbs/tag.php?q=' + tag + '&page={}'
        global avnumlist_tag
        del avnumlist_tag[:]
        if len(is_empty) == 0:
            chiyak.sendMessage(check_id(bot, update), "검색중이에요!")
            text = ""
            count = 0
            for i in range(1,11):
                url = base_url.format(i)
                req_search = requests.get(url)
                html_search = req_search.text
                soup_search = BeautifulSoup(html_search, 'html.parser')
                is_empty = soup_search.select('body > div#thema_wrapper > div.wrapper > div#content_wrapper > div.content > div.at-content > div#at-wrap > div#at-main > div.tagbox-media > p')
                if len(is_empty) != 0:
                    if count != 0:
                        avnumlist_tag.append(text)
                        text = ''
                        count = 0
                    break
                avlist = soup_search.select('body > div#thema_wrapper > div.wrapper > div#content_wrapper > div.content > div.at-content > div#at-wrap > div#at-main > div.tagbox-media > div.media > div.media-body > div.media-heading > a > b')
                for avnum in avlist:
                    text = text + "\n" + avnum.text
                    count += 1
                    if count == 20:
                        avnumlist_tag.append(text)
                        text = ''
                        count = 0
                if count != 0 and i == 10:
                    avnumlist_tag.append(text)
                    text = ''
                    count = 0
            leng = len(avnumlist_tag)
            if leng < 5:
                for i in range(leng + 1, 6):
                    avnumlist_tag.append("이 페이지에는 아무것도 없어요!")
                    
            button_list = build_button(["첫번째", "두번째", "세번째", "네번째", "다섯번째", "그만보기"])
            show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
            update.message.reply_text("원하는 페이지를 선택하세요!", reply_markup=show_markup)
        else:
            chiyak.sendMessage(check_id(bot, update), "검색결과가 하나도 없어요!")
'''
#AVSEE 제목으로 영상 검색 기능
def name_search_command(bot, update):
    if update.message.text in '/namesearch':
        update.message.reply_text('검색할 배우 이름을 뒤에 써주세요! 최소 2글자 이상이여야 해요!\n예시)/namesearch 아스카 키라라\n')
    else:
        name = update.message.text[11:]
        name = name.strip()
        name = name.replace(' ', '+')
        req_search_name = requests.get('https://avsee04.tv/bbs/search.php?gr_id=video&sfl=wr_subject&stx=' + name)
        html_name = req_search_name.text
        soup_name = BeautifulSoup(html_name, 'html.parser')
        is_empty = soup_name.select('body > div#thema_wrapper > div.wrapper > div#content_wrapper > div.content > div.at-content > div#at-wrap > div#at-main > p')
        base_url = 'https://avsee04.tv/bbs/search.php?gr_id=video&sfl=wr_subject&stx=' + name + '&page={}'
        global avnumlist_name
        del avnumlist_name[:]
        if len(is_empty) == 0:
            chiyak.sendMessage(check_id(bot, update), "검색중이에요!")
            text = ""
            count = 0
            for i in range(1,11):
                url = base_url.format(i)
                req_search = requests.get(url)
                html_search = req_search.text
                soup_search = BeautifulSoup(html_search, 'html.parser')
                avlist = soup_search.select('body > div#thema_wrapper > div.wrapper > div#content_wrapper > div.content > div.at-content > div#at-wrap > div#at-main > div.search-media > div.media > div.media-body > div.media-heading > a > b')
                for avnum in avlist:
                    is_name = avnamecheck.search(avnum.text)
                    if is_name:
                        text = text + "\n" + avnum.text
                        count += 1
                        if count == 10:
                            avnumlist_name.append(text)
                            text = ''
                            count = 0
                if count != 0 and i == 10:
                    avnumlist_name.append(text)
                    text = ''
                    count = 0
            leng = len(avnumlist_name)
            if leng < 5:
                for i in range(leng + 1, 6):
                    avnumlist_name.append("이 페이지에는 아무것도 없어요!")

            button_list = build_button(["one", "two", "three", "four", "five", "그만보기"])
            show_markup = InlineKeyboardMarkup(build_menu(button_list, len(button_list) - 1))
            update.message.reply_text("원하는 페이지를 선택하세요!", reply_markup=show_markup)
        else:
            chiyak.sendMessage(check_id(bot, update), "검색결과가 하나도 없어요!")
'''
#AVSEE 품번의 영상링크, 정보 가져오는 기능
def getav_command(bot, update):
    if update.message.text in '/getav':
        update.message.reply_text('명령어 뒤에 품번을 써주세요!\n예시)/getav SAM-572')
    else:
        text = update.message.text[6:]
        text = text.strip()
        req_get_target = requests.get('https://avsee04.tv/bbs/search.php?gr_id=video&sfl=wr_subject&stx=' + text)
        html_target = req_get_target.text
        soup_target = BeautifulSoup(html_target, 'html.parser')
        is_empty = soup_target.select('body > div#thema_wrapper > div.wrapper > div#content_wrapper > div.content > div.at-content > div#at-wrap > div#at-main > p')
        if len(is_empty) == 0:
            target = soup_target.select('body > div#thema_wrapper > div.wrapper > div#content_wrapper > div.content > div.at-content > div#at-wrap > div#at-main > div.search-media > div.media > div.media-body > a')[0]
            target_url = 'https://avsee04.tv/bbs/' + target.get('href')[2:]
            req_get_av = requests.get(target_url)
            html_av = req_get_av.text
            soup_av = BeautifulSoup(html_av, 'html.parser')
            avinfo = soup_av.select('body > div#thema_wrapper > div.wrapper > div#content_wrapper > div.content > div.at-content > div#at-wrap > div#at-main > div.view-wrap > section > article > div.view-padding > div.view-content')[0].text
            avinfo = avinfo.strip()
#           driver = webdriver.Chrome('./chromedriver')
#           driver.get(target_url)
#           driver.implicitly_wait(30)
#           avframe = driver.find_element_by_tag_name('iframe')
#           driver.switch_to_frame(avframe)
#           req_video = driver.page_source
#           driver.quit()
#           soup_video = BeautifulSoup(req_video, 'html.parser')
#           av = soup_video.select('body > div#player > div.jw-wrapper.jw-reset > div.jw-media.jw-reset > video.jw-video.jw-reset')[0].get('src')
            chiyak.sendMessage(check_id(bot,update), avinfo + '\n\n' + target_url)
        else:
            chiyak.sendMessage(check_id(bot,update), "이 사이트에는 없는 영상이에요!")

#선택장애 치료 기능
def pick_command(bot, update):
    is_correct = update.message.text.split(' ', 1)
    if len(is_correct) == 1:
        update.message.reply_text('구분자(공백, 콤마 등)를 포함해 /pick 뒤에 써주세요!\nex) /pick 1,2,3,4 or /pick 1 2 3 4')
    else:
        text = is_correct[1]
        text = text.strip()
        if ',' in text:
            picklist = text.split(',')
            pick = random.randint(0, len(picklist))
            update.message.reply_text(picklist[pick])
        else:
            picklist = text.split(' ')
            pick = random.randint(0, len(picklist))
            update.message.reply_text(picklist[pick])
    '''if update.message.text in '/pick@chiyakbot':
        update.message.reply_text('구분자(공백, 콤마 등)를 포함해 /pick 뒤에 써주세요!\nex) /pick 1,2,3,4 or /pick 1 2 3 4')
    else:
        text = update.message.text[5:]
        text = text.strip()
        picklist = re.findall(r"[\w']+", text)
        pick = random.randint(0,len(picklist))
        update.message.reply_text(picklist[pick])'''

#채팅방 퇴장 기능
def exit_command(bot, update):
    if update.message.from_user.id == 46674072:
        update.message.reply_text("안녕히 계세요!")
        chiyak.core.leave_chat(update.message.chat.id)

def delMessage_command(bot, update):
    if update.message.from_user.id == 46674072:
        target_id = update.message.reply_to_message.message_id
        target_group = update.message.reply_to_message.chat.id
        chiyak.core.deleteMessage(target_group, target_id)

#메세지 감지가 필요한 기능들
def messagedetecter(bot, update):
    #채팅창 계산기 기능
    is_calc = calc_p.match(update.message.text)
    if is_calc:
        result = eval(update.message.text[1:])
        update.message.reply_text(result)

    #확률대답 기능
    if '확률은?' in update.message.text:
        n = random.randint(0,100)
        update.message.reply_text("{}퍼센트".format(n))
    
    #소라고둥님
    if '마법의 소라고둥님' in update.message.text:
        n = random.randint(0,1)
        update.message.reply_text(yn[n])

chiyak = chatbotmodel.chiyakbot()
chiyak.add_cmdhandler('help', help_command)
chiyak.add_cmdhandler('about', about_command)
chiyak.add_cmdhandler('stop', stop_command)
chiyak.add_cmdhandler('dogfood', dogfood_command)
chiyak.add_callhandler(dogfood_callback)
chiyak.add_cmdhandler('update', dogfood_update)
chiyak.add_cmdhandler('pick', pick_command)
chiyak.add_cmdhandler('exit', exit_command)
chiyak.add_messagehandler(messagedetecter)
chiyak.add_cmdhandler('tagrank', rank_tag_command)
chiyak.add_cmdhandler('avsearch', av_search_command)
#chiyak.add_cmdhandler('namesearch', name_search_command)
chiyak.add_cmdhandler('getav', getav_command)
chiyak.add_cmdhandler('delMessage', delMessage_command)
chiyak.start()
