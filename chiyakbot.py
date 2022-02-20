import chatbotmodel
from telegram import InputMediaPhoto
import re
import random
from lib import checkPickup, sauceNAO, hitomi, reminder, exchange, namusearch, papago, corona
import boto3
import json
from inko import Inko
import prettytable

# 전역변수

chiyak = chatbotmodel.chiyakbot()
calc_p = re.compile('^=[0-9+\-*/%!^( )]+')
isURL = re.compile(
    'http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
available_modeltype = ['ipad_pro', 'ipad_air',
                       'ipad_mini', 'ipad_10_2', 'iphone_12',
                       'iphone_12_pro', 'iphone_se', 'iphone_xr',
                       'iphone_11']
myInko = Inko()
comprehend = boto3.client(service_name='comprehend', region_name='ap-northeast-2',
                          aws_access_key_id='AKIA2475NDPROSZBLDGE',
                          aws_secret_access_key='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')
helpText = """/를 붙여서 사용해야하는 기능들

/about 자기소개
/pick 구분자(, | . 등등)과 함께 입력하면 하나를 골라주는 기능

/cp [modelcode?] [modeltype?] 모델코드 입력하면 애플스토어 구매/픽업 가능여부 알려주는 기능
modelcode가 없으면 기본값은 5세대 12.9 128 셀룰러 스페이스그레이 모델
modeltype이 없으면 기본값은 ipad_pro, 가능한 모델타입은 아래와 같음
{0}

/cpr [modelcode] 모델코드 입력하면 애플스토어 픽업 가능할때 해당 채팅방에 알려주는 기능
modelcode가 없으면 기본값은 5세대 12.9 128 셀룰러 스페이스그레이 모델

/cpd [modelcode] 모델코드 입력하면 픽업 감시 취소
modelcode가 없으면 5세대 12.9 128 셀룰러 스페이스 그레이 예약한것 취소

/qr [url] url을 qr코드 이미지로 변환해주는 기능

/roll [%dd%d] '정수1' + d + '정수2' 형식으로 쓰면 정수2각형 주사위 정수1개만큼 굴려서 결과 출력
기반코드: https://github.com/superfluite/trpg-dice-bot

/ds 답장을 사용한 메세지의 긍정/부정에 따라 괜찮아요/나빠요 출력
aws는 대개 나쁘다고 생각하는듯함.

/en2ko(ko2en) [some string] 영어로 쓴 문자열이나 한글로 쓴 문자열을 각각 영어, 한글로 변환
ex) /en2ko dksl -> 아니, /ko2en ㅗ디ㅣㅐ -> hello

/simimg 답장을 사용한 메세지의 사진 출처를 찾아주는 기능
sauceNAO api를 사용하므로 씹덕짤만 잘찾음.

'='다음에 수식을 쓰면 계산해주는 계산기
ex) =1+1 or =2*2

'확률은?'을 뒤에 붙이면 랜덤확률을 말해주는 기능
ex) 오늘 일론머스크가 또 헛소리할 확률은?

'마법의 소라고둥님'으로 시작하면 그래, 아니중 하나로 대답해주는 소라고둥님
ex) 마법의 소라고둥님 오늘 도지가 화성에 갈까요?
""".format(available_modeltype)

cities = {
    '8': '경기',
    '0': '서울',
    '2': '인천',
    '3': '대구',
    '4': '광주',
    '1': '부산',
    '12': '경북',
    '13': '경남',
    '11': '충남',
    '15': '전남',
    '5': '대전',
    '14': '전북',
    '10': '충북',
    '9': '강원',
    '6': '울산',
    '16': '제주',
    '7': '세종',
    '17': '검역'
}

# deprecated func alert


def deprecated(update):
    update.message.reply_text('저런, 이 기능은 더이상 지원되지 않아요!')


# 유저 chat_id 가져오기


def check_id(update, context):
    try:
        id = update.message.chat.id
        # print(id)
        return id
    except:
        id = update.channel_post.chat.id
        return id

# 유저 닉네임 가져오기


def check_nickname(update, context):
    try:
        nickname = update.message.from_user.first_name
        # print(nickname)
        return nickname
    except:
        nickname = update.channel_post.from_user.first_name
        return nickname

# 도움말 기능


def help_command(update, context):
    id = check_id(update, context)
    chiyak.sendMessage(id, "안녕하세요, " + check_nickname(update,
                       context) + "님. 저는 아래 목록에 있는 일을 할 수 있어요!")
    chiyak.sendMessage(id, helpText)

# 자기소개 기능


def about_command(update, context):
    chiyak.sendMessage(check_id(update, context), "저는 다기능 대화형 봇인 치약봇이에요.")

# 정지 기능


def stop_command(update, context):
    if update.message.from_user.id == chiyak.id:
        chiyak.sendMessage(check_id(update, context), "안녕히주무세요!")
        chiyak.stop()

# 선택장애 치료 기능


def pick_command(update, context):
    is_correct = update.message.text.split(' ', 1)
    if len(is_correct) <= 1:
        update.message.reply_text(
            '구분자(공백, 콤마 등)를 포함해 /pick 뒤에 써주세요!\nex) /pick 1,2,3,4 or /pick 1 2 3 4')
    else:
        text = is_correct[1]
        text = text.strip()
        if ',' in text:
            picklist = text.split(',')
            pick = random.choice(picklist)
            update.message.reply_text(pick)

        elif ' ' in text:
            picklist = text.split(' ')
            pick = random.choice(picklist)
            update.message.reply_text(pick)

# 채팅방 퇴장 기능


def exit_command(update, context):
    if update.message.from_user.id == chiyak.id:
        update.message.reply_text("안녕히 계세요!")
        chiyak.core.leave_chat(update.message.chat.id)

# 메세지 삭제 기능


def delMessage_command(update, context):
    if update.message.from_user.id == chiyak.id:
        target_id = update.message.reply_to_message.message_id
        target_group = update.message.reply_to_message.chat.id
        chiyak.core.deleteMessage(target_group, target_id)

# 메세지 한영변환


def enko_command(update, context):
    if update.message.reply_to_message is not None:
        update.message.reply_text(myInko.en2ko(
            update.message.reply_to_message.text))
    else:
        text = update.message.text.split(' ', 1)
        if len(text) <= 1:
            update.message.reply_text(
                '변환하고자 하는 메세지에 답장을 달거나, 명령어 뒤에 변환하고자 하는 문자열을 써주세요!\n ex)/en2ko dksl')
        else:
            update.message.reply_text(myInko.en2ko(text[1]))


def koen_command(update, context):
    if update.message.reply_to_message is not None:
        update.message.reply_text(myInko.ko2en(
            update.message.reply_to_message.text))
    else:
        text = update.message.text.split(' ', 1)
        if len(text) <= 1:
            update.message.reply_text(
                '변환하고자 하는 메세지에 답장을 달거나, 명령어 뒤에 변환하고자 하는 문자열을 써주세요!\n ex)/ko2en ㅗ디ㅣㅐ')
        else:
            update.message.reply_text(myInko.ko2en(text[1]))


def detectSentiment_command(update, context):
    if update.message.reply_to_message is not None:
        if update.message.reply_to_message.text is not None:
            result = comprehend.detect_sentiment(
                Text=update.message.reply_to_message.text, LanguageCode='ko')
            chiyak.core.sendMessage(
                chat_id=update.message.chat_id,
                text='나빠요' if result['SentimentScore']['Positive'] < result['SentimentScore']['Negative'] else '괜찮아요',
                reply_to_message_id=update.message.reply_to_message.message_id)
        else:
            update.message.reply_text('텍스트에만 사용 해주세요!')
    else:
        user_input = update.message.text.split(' ', 1)
        if len(user_input) <= 1:
            update.message.reply_text(
                '원하는 텍스트에 답장을 걸고 사용하거나, 명령어 뒤에 원하는 문자열을 써주세요!')
            return
        else:
            result = comprehend.detect_sentiment(
                Text=user_input[1], LanguageCode='ko')
            update.message.reply_text(
                '나빠요' if result['SentimentScore']['Positive'] < result['SentimentScore']['Negative'] else '괜찮아요')


def roll_command(update, context):
    dice_text = update.message.text.split(' ')[-1]
    # print(dice_text)
    if re.match(r'^\d*[dD]\d*$', dice_text):
        text_result = dice_text.split('d')
        cnt = int(text_result[0])
        upper = int(text_result[1])
    else:
        cnt = 2
        upper = 6
    #print(cnt, upper)
    if cnt > 20:
        reply = '주사위가 너무 많습니다'
    elif upper > 120:
        reply = '주사위 면이 너무 많습니다'
    else:
        result = roll(cnt, upper)
        # print(result)
        reply = (f'전체 🎲: {", ".join(str(i) for i in result)} \n'
                 f'결과: {sum(result)}')
    update.message.reply_text(reply)


def roll(cnt, upper):
    results = []
    for i in range(0, cnt):
        results.append(random.randint(1, upper))
    return results


def makeQR_command(update, context):
    base_url = 'https://chart.apis.google.com/chart?cht=qr&chs=300x300&chl='
    if update.message.reply_to_message is not None:
        if update.message.reply_to_message.text is not None:
            urls = isURL.findall(update.message.reply_to_message.text)
            if urls != [] and len(urls) == 1:
                chiyak.core.send_photo(
                    chat_id=update.message.chat_id, photo=base_url + urls[0])
            elif urls != [] and len(urls) > 1:
                result_urls = []
                for target_url in urls:
                    result_urls.append(InputMediaPhoto(base_url + target_url))
                chiyak.core.send_media_group(
                    chat_id=update.message.chat_id, media=result_urls)
            else:
                update.message.reply_text('url을 찾을 수 없어요!')
        else:
            update.message.reply_text('텍스트에만 사용 해주세요!')
    else:
        user_input = update.message.text.split(' ', 1)[1]
        urls = isURL.findall(user_input)
        if urls != [] and len(urls) == 1:
            chiyak.core.send_photo(
                chat_id=update.message.chat_id, photo=base_url + urls[0])
        elif urls != [] and len(urls) > 1:
            result_urls = []
            for target_url in urls:
                result_urls.append(InputMediaPhoto(base_url + target_url))
            chiyak.core.send_media_group(
                chat_id=update.message.chat_id, media=result_urls)
        else:
            update.message.reply_text('url을 찾을 수 없어요!')


def simimg_command(update, context):
    if update.message.reply_to_message.photo != []:
        img_info = chiyak.core.getFile(
            update.message.reply_to_message.photo[-1].file_id)
        sitename, best_sitelink, similarity, long_remaining = sauceNAO.get_similarity(
            img_info)
        update.message.reply_text('''
[*{0}*]({1}) 에서 가장 비슷한 이미지를 발견했어요\\!
유사도: *{2}*
남은 일일 검색횟수: *{3}*
    '''.format(sitename, best_sitelink, similarity, long_remaining), parse_mode='MarkdownV2')
    else:
        update.message.reply_text('사진이 없는거같아요! 사진에 답장을 써주세요!')


def get_hitomi_info_command(update, context):
    user_input = update.message.text.split(' ', 1)
    if len(user_input) <= 1:
        chiyak.sendMessage(update.message.chat_id, '번호가 없는거같아요!')
        return
    else:
        result = hitomi.get_info(user_input[1])
        chiyak.core.sendMessage(chat_id=update.message.chat_id, text='''
제목: {}
게시일: {}
언어: {}
종류: {}

바로가기: {}

만족하시나요 휴-먼?
'''.format(result['title'], result['date'], result['language'], result['type'], result['link']) if result['result'] == 'success' else result['message'])


def get_exchange_command(update, context):
    result = ''
    user_input = update.message.text.split(' ', 1)
    table = prettytable.PrettyTable(['CODE', 'KRW'])
    table.align['CODE'] = 'l'
    table.align['KRW'] = 'l'
    if len(user_input) <= 1:
        exchange_data = exchange.request_info()
        for item in exchange_data['data']:
            # print(item)
            table.add_row([item['currencyCode'], item['basePrice']])
        result = table.get_string()
    else:
        input_code = user_input[1].upper()
        exchange_data = exchange.request_info(input_code)
        if exchange_data['result']:
            for item in exchange_data['data']:
                # print(item)
                table.add_row([item['currencyCode'], item['basePrice']])
            result = table.get_string()
        else:
            message = exchange_data['message']
            update.message.reply_text(f'{message}')
    # print(result)
    update.message.reply_text(f'<pre>{result}</pre>', parse_mode='HTML')


def calc_exchange_command(update, context):
    result = None
    user_input = update.message.text.split(' ')
    if len(user_input) <= 2:
        update.message.reply_text('뭔가 빠진거같아요! 다시 시도해주세요!')
    else:
        input_code = user_input[1].upper()
        exchange_data = exchange.request_info(input_code)
        input_cur = round(float(user_input[2].replace(',', '')))
        format_cur = format(input_cur, ",")
        if exchange_data['result']:
            try:
                item = exchange_data['data'][0]
                result = format(
                    round(float(item['basePrice']) * input_cur / int(item['currencyUnit'])), ",")
                update.message.reply_text(
                    f'{format_cur} {input_code} ≈ {result} KRW')
            except:
                update.message.reply_text(
                    '계산중에 오류가 발생했어요! 지원하지 않는 통화코드거나 값을 잘못 쓰신거같아요! 다시 시도해보세요.')
                return
        else:
            message = exchange_data['message']
            update.message.reply_text(f'{message}')


def kospnamu_command(update, context):
    deprecated(update)
    #rank, rank_status = kospnamu.get_kospnamu()
    #res_text = '떨어진다 싶을때는 개 추해요' if '하락' in rank_status else '갇힌분은 어서 돔황챠'
    #update.message.reply_text(f'피나무 한국 {rank}, {rank_status}\n{res_text}')

def namesearch_command(update, context):
    deprecated(update)
    #text = update.message.text.split(' ', 1)
    #if len(text) <= 1:
    #    update.message.reply_text(
    #        '명령어 뒤에 검색하고자 하는 단어를 써주세요!\n예시: /namu 나무')
    #else:
    #    result = namusearch.search_namu(text[1])
    #    update.message.reply_text(result)

def papago_command(update, context):
    if update.message.reply_to_message is not None:
        if update.message.reply_to_message.text is not None:
            text = update.message.reply_to_message.text
            cleaned_text = text.replace('\n', ' ')
            result = papago.get_translate(cleaned_text)
            update.message.reply_text(result)
    else:
        text = update.message.text.split(' ', 1)
        if len(text) <= 1:
            update.message.reply_text(
                '명령어 뒤에 번역하고자 하는 문장을 쓰거나 답장으로 알려주세요!\n예시: /papago Heads up that my son\'s school closed for in-person learning for ten days, starting this afternoon, because of a covid outbreak that began at the end of last week, and all kids and staff who were in that building within the past 48 hours are advised to self-isolate for five days and then get a covid test.')
        else:
            cleaned_text = text[1].replace('\n', ' ')
            result = papago.get_translate(cleaned_text)
            update.message.reply_text(result)

def corona_today_total_command(update, context):
    result = corona.get_today_info()
    update.message.reply_text(
        f"{result['last_updated']} 기준\n \
오늘 확진자수: {result['live']['today']}\n \
어제 확진자수: {result['live']['yesterday']}\n \
1주전 확진자수: {result['live']['weekAgo']}\n \
2주전 확진자수: {result['live']['twoWeeksAgo']}\n \
한달전 확진자수: {result['live']['monthAgo']}\n"
    )

def corona_today_city_command(update, context):
    result = corona.get_today_info()
    rep_text = f"{result['last_updated']} 기준\n"
    for item in result['sorted_cities']:
        rep_text += f'{cities[item[0]]} : {item[1][0]}, 증감 : {item[1][1]}\n'
    update.message.reply_text(
        rep_text
    )


# 메세지 감지가 필요한 기능들


def messagedetecter(update, context):
    try:
        # 채팅창 계산기 기능
        is_calc = calc_p.match(update.message.text)
        if is_calc:
            result = round(float(eval(update.message.text[1:])), 2)
            update.message.reply_text(result)
        else:
            # 확률대답 기능
            if '확률은?' in update.message.text:
                n = random.randint(0, 100)
                update.message.reply_text("{}퍼센트".format(n))

            # 소라고둥님
            if '마법의 소라고둥님' in update.message.text:
                update.message.reply_text(random.choice(['그래.', '아니.']))
    except Exception as e:
        print(e)


chiyak.add_cmdhandler('coronacity', corona_today_city_command)
chiyak.add_cmdhandler('coronatoday', corona_today_total_command)
chiyak.add_cmdhandler('papago', papago_command)
chiyak.add_cmdhandler('namu', namesearch_command)
chiyak.add_cmdhandler('kospn', kospnamu_command)
chiyak.add_cmdhandler('exchc', calc_exchange_command)
chiyak.add_cmdhandler('exch', get_exchange_command)
chiyak.add_cmdhandler('rmdl', reminder.start_remind_loop)
chiyak.add_cmdhandler('remind', reminder.reminder_register)
chiyak.add_cmdhandler('htm', get_hitomi_info_command)
chiyak.add_cmdhandler('qr', makeQR_command)
chiyak.add_cmdhandler('roll', roll_command)
chiyak.add_cmdhandler('simimg', simimg_command)
chiyak.add_cmdhandler('ds', detectSentiment_command)
chiyak.add_cmdhandler('ko2en', koen_command)
chiyak.add_cmdhandler('en2ko', enko_command)
chiyak.add_cmdhandler('cp', checkPickup.checkPickup_command)
chiyak.add_cmdhandler('cpl', checkPickup.checkPickupLoop)
chiyak.add_cmdhandler('cpr', checkPickup.checkPickupRegister)
chiyak.add_cmdhandler('cpd', checkPickup.checkPickupDelete)
chiyak.add_cmdhandler('help', help_command)
chiyak.add_cmdhandler('about', about_command)
chiyak.add_cmdhandler('stop', stop_command)
chiyak.add_cmdhandler('pick', pick_command)
chiyak.add_cmdhandler('exit', exit_command)
chiyak.add_cmdhandler('del', delMessage_command)
chiyak.add_inlinequeryhandler(namusearch.inlinequeryhandler)
chiyak.add_conversationHandler(reminder.rm_remind_handler)
chiyak.add_messagehandler(messagedetecter)

chiyak.start()
