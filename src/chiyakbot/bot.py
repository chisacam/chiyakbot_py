import os
import random
import re
import sys
from typing import Final, List

from dotenv import load_dotenv
from telegram import BotCommand, InputMediaPhoto, Message, Update, error
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
    MessageHandler,
    filters,
)

from .chatbots import (
    AbstractChatbotModel,
    BaseAnswerMachine,
    CommandAnswerMachine,
    InlineQueryAnswerMachine,
    MessageAnswerMachine,
)
from .utils import privileged_message

load_dotenv()

# 전역변수

calc_p = re.compile("^=[0-9+\-*/%!^( )]+")
is_url = re.compile(
    "http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

HELP_TEXT: Final[
    str
] = """/를 붙여서 사용해야하는 기능들

/qr [url] url을 qr코드 이미지로 변환해주는 기능
/roll [%dd%d] '정수1' + d + '정수2' 형식으로 쓰면 정수2각형 주사위 정수1개만큼 굴려서 결과 출력

'='다음에 수식을 쓰면 계산해주는 계산기
ex) =1+1 or =2*2

'확률은?'을 뒤에 붙이면 랜덤확률을 말해주는 기능
ex) 오늘 일론머스크가 또 헛소리할 확률은?

'마법의 소라고둥님'으로 시작하면 그래, 아니중 하나로 대답해주는 소라고둥님
ex) 마법의 소라고둥님 오늘 도지가 화성에 갈까요?
""".format()

# deprecated func alert

async def deprecated(
    update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
):
    await message.reply_text("저런, 이 기능은 더이상 지원되지 않아요!")


class IntrinsicChatbotModel(AbstractChatbotModel):
    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(self.help_command, "help", description="도움말"),
            CommandAnswerMachine(self.about_command, "about", description="자기소개"),
            CommandAnswerMachine(self.stop_command, "stop"),
            CommandAnswerMachine(
                self.pick_command,
                "pick",
                description="구분자(, | . 등등)과 함께 입력하면 하나를 골라주는 기능",
            ),
            CommandAnswerMachine(self.exit_command, "exit"),
            CommandAnswerMachine(self.del_message_command, "del"),
            CommandAnswerMachine(self.here_command, "here"),
            CommandAnswerMachine(self.get_reply_command, "getmsg"),
            CommandAnswerMachine(self.get_message_id_command, "getmsgid"),
            CommandAnswerMachine(self.makeQR_command, "qr"),
        ]

    # 유저 chat_id 가져오기
    def check_id(self, update: Update, message: Message):
        try:
            id = message.chat.id
            # print(id)
            return id
        except:
            id = update.channel_post.chat.id
            return id

    # 유저 닉네임 가져오기

    def check_nickname(self, update: Update, message: Message):
        try:
            nickname = message.from_user.first_name
            # print(nickname)
            return nickname
        except:
            nickname = update.channel_post.from_user.first_name
            return nickname

    # 도움말 기능

    async def help_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        id = self.check_id(update, message)
        await self.bot.send_message(
            id,
            f"안녕하세요, {self.check_nickname(update, message)}님. 저는 아래 목록에 있는 일을 할 수 있어요!",
        )
        await self.bot.send_message(id, HELP_TEXT)

    # 자기소개 기능

    async def about_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        await self.bot.send_message(
            self.check_id(update, message), "저는 다기능 대화형 봇인 치약봇이에요."
        )

    # 정지 기능

    @privileged_message
    async def stop_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        await self.bot.send_message(self.check_id(update, message), "안녕히주무세요!")
        exit(0)

    # 선택장애 치료 기능

    async def pick_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        is_correct = (message.text or "").split(" ", 1)
        if len(is_correct) <= 1:
            await message.reply_text(
                "구분자(공백, 콤마 등)를 포함해 /pick 뒤에 써주세요!\nex) /pick 1,2,3,4 or /pick 1 2 3 4"
            )
        else:
            text = is_correct[1]
            text = text.strip()
            if "," in text:
                picklist = text.split(",")
                pick = random.choice(picklist)
                await message.reply_text(pick)

            elif " " in text:
                picklist = text.split(" ")
                pick = random.choice(picklist)
                await message.reply_text(pick)

    # 채팅방 퇴장 기능

    @privileged_message
    async def exit_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        await message.reply_text("안녕히 계세요!")
        await self.bot.leave_chat(message.chat.id)

    # 메세지 삭제 기능

    @privileged_message
    async def del_message_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        if message.reply_to_message is None:
            return
        target_id = message.reply_to_message.message_id
        target_group = message.reply_to_message.chat.id
        await self.bot.delete_message(target_group, target_id)

    async def here_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        await self.bot.send_message(message.chat.id, "/wol@Wolfpaw_bot")

    async def get_reply_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        input_text = (message.text or "").split(" ", 1)
        if len(input_text) > 1 and input_text[1].isdigit():
            try:
                await self.bot.send_message(
                    message.chat.id,
                    f"{input_text[1]}번째 메세지에요!",
                    reply_to_message_id=input_text[1],
                )
            except error.BadRequest:
                await message.reply_text("저런, 해당하는 메세지가 없네요!")
        else:
            await message.reply_text("저런, id가 올바르지 않네요! 숫자로만 구성해주세요!")

    async def get_message_id_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        if message.reply_to_message is not None:
            await message.reply_text(
                f"이 메세지의 id는 {message.reply_to_message.message_id} 이에요!"
            )
        else:
            await message.reply_text("저런, 답장형식이 아니네요! 원하는 메세지에 답장으로 사용해주세요!")

    async def roll_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        dice_text = (message.text or "").split(" ")[-1]
        # print(dice_text)
        if re.match(r"^\d*[dD]\d*$", dice_text):
            text_result = dice_text.split("d")
            cnt = int(text_result[0])
            upper = int(text_result[1])
        else:
            cnt = 2
            upper = 6
        # print(cnt, upper)
        if cnt > 20:
            reply = "주사위가 너무 많습니다"
        elif upper > 120:
            reply = "주사위 면이 너무 많습니다"
        else:
            result = self.roll(cnt, upper)
            # print(result)
            reply = f'전체 🎲: {", ".join(str(i) for i in result)} \n' f"결과: {sum(result)}"
        await message.reply_text(reply)

    def roll(self, cnt, upper):
        results = []
        for i in range(0, cnt):
            results.append(random.randint(1, upper))
        return results

    async def makeQR_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        base_url = "https://chart.apis.google.com/chart?cht=qr&chs=300x300&chl="
        if message.reply_to_message is not None:
            if message.reply_to_message.text is not None:
                urls = is_url.findall(message.reply_to_message.text)
                if urls != [] and len(urls) == 1:
                    await self.bot.send_photo(
                        chat_id=message.chat.id, photo=base_url + urls[0]
                    )
                elif urls != [] and len(urls) > 1:
                    result_urls = []
                    for target_url in urls:
                        result_urls.append(InputMediaPhoto(base_url + target_url))
                    await self.bot.send_media_group(
                        chat_id=message.chat.id, media=result_urls
                    )
                else:
                    await message.reply_text("url을 찾을 수 없어요!")
            else:
                await message.reply_text("텍스트에만 사용 해주세요!")
        else:
            user_input = (message.text or "").split(" ", 1)[1]
            urlOBs = is_url.findall(user_input)
            if urls != [] and len(urls) == 1:
                await self.bot.send_photo(
                    chat_id=message.chat.id, photo=base_url + urls[0]
                )
            elif urls != [] and len(urls) > 1:
                result_urls = []
                for target_url in urls:
                    result_urls.append(InputMediaPhoto(base_url + target_url))
                await self.bot.send_media_group(
                    chat_id=message.chat.id, media=result_urls
                )
            else:
                await message.reply_text("url을 찾을 수 없어요!")


async def post_init(app: Application) -> None:
    from .chatbots import defined_models

    owner_id = os.getenv("ADMIN_TG_ID")
    assert owner_id is not None

    my_commands: List[BotCommand] = []
    for model_cls in [IntrinsicChatbotModel, *defined_models]:
        m = model_cls(app.bot, owner_id)
        for handler in m.list_available_handlers():
            if isinstance(handler, CommandAnswerMachine):
                app.add_handler(CommandHandler(handler.command, handler.handler))
                my_commands.append(
                    BotCommand(handler.command, handler.description or handler.command)
                )
            elif isinstance(handler, InlineQueryAnswerMachine):
                app.add_handler(InlineQueryHandler(handler.handler))
            elif isinstance(handler, MessageAnswerMachine):
                app.add_handler(
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handler)
                )
            print("Registered", handler)
        for conversation in m.list_available_conversations():
            app.add_handler(conversation)

    await app.bot.set_my_commands(my_commands)


if __name__ == "__main__":
    token = (
        os.getenv("TG_TOKEN")
        if sys.argv[1] != "develop"
        else os.getenv("TG_BETA_TOKEN")
    )
    owner_id = os.getenv("ADMIN_TG_ID")
    if token is None:
        print("token is not set")
        exit(1)
    if owner_id is None:
        print("admin's telegram id is not set")
        exit(1)

    app = Application.builder().token(token).post_init(post_init).build()

    app.run_polling()
