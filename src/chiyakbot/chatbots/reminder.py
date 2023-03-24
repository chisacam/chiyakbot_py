import asyncio
import datetime
import json
import os.path
import re
import uuid
from typing import Any, List, Mapping, Optional

from pytz import timezone
from telegram import (Bot, KeyboardButton, Message, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from chiyakbot.utils import privileged_message

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine

file_path = "./reminded.json"
is_only_time = re.compile(
    "^((202[0-9]{1})(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01]))?((0[0-9]|1[0-9]|2[0-3])([0-5][0-9])){1}$"
)
DREMIND = 0


class ReminderModel(AbstractChatbotModel):
    name = "reminder"
    reminder_task: Optional[asyncio.Task]
    alert_users: List[dict]

    def __init__(self, bot: Bot, owner_id: str) -> None:
        super().__init__(bot, owner_id)
        self.reminder_task = None
        self.alert_users = []
        if os.path.exists(file_path):
            with open(file_path, "r") as json_file:
                self.alert_users = json.load(json_file)

    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(self.start_remind_loop, "rmdl"),
            CommandAnswerMachine(self.reminder_register, "remind"),
        ]

    def list_available_conversations(self) -> List[ConversationHandler]:
        return [
            ConversationHandler(
                [
                    CommandHandler(
                        "dremind",
                        BaseAnswerMachine.message_handler_generator(
                            self.reminder_delete_command
                        ),
                    )
                ],
                {
                    DREMIND: [
                        MessageHandler(
                            filters.TEXT,
                            BaseAnswerMachine.message_handler_generator(
                                self.remind_delete
                            ),
                        )
                    ]
                },
                [
                    CommandHandler(
                        "drcancel",
                        BaseAnswerMachine.message_handler_generator(
                            self.remind_delete_error
                        ),
                    )
                ],
            )
        ]

    async def reminder(self):
        while True:
            try:
                for remind_task in self.alert_users[:]:
                    now = datetime.datetime.now(timezone("Asia/Seoul")).strftime(
                        "%Y%m%d%H%M"
                    )
                    if now >= remind_task["remind_date"]:
                        await self.bot.send_message(
                            chat_id=remind_task["remind_chat_id"],
                            reply_to_message_id=remind_task["remind_message_id"],
                            text=f'다시 확인해보실 시간이에요!\n메모: {remind_task["remind_text"]}',
                        )
                        self.alert_users.remove(remind_task)

                def _write():
                    with open(file_path, "w") as outfile:
                        json.dump(self.alert_users, outfile, indent=4, ensure_ascii=False)

                await asyncio.get_running_loop().run_in_executor(None, _write)
                await asyncio.sleep(10)
            except Exception as e:
                print(e)
                break

    @privileged_message
    async def start_remind_loop(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        await self.bot.send_message(message.chat.id, "리마인드 스레드 시작!")
        if self.reminder_task:
            self.reminder_task.cancel()
            await self.reminder_task

        self.reminder_task = asyncio.create_task(self.reminder())

    async def reminder_register(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        if message.from_user is None:
            return
        user_id = message.from_user.id
        chat_id = message.chat.id
        remind_text_id = message.message_id
        user_input = (message.text or "").split(" ", 2)
        if message.reply_to_message is not None:
            if message.reply_to_message.text is not None:
                if len(user_input) > 1:
                    result = self.regist(
                        chat_id,
                        user_id,
                        message.reply_to_message.text,
                        remind_text_id,
                        user_input[1].strip(),
                        "reply",
                    )
                    await message.reply_text(result["message"])
                else:
                    await message.reply_text(
                        "언제 다시 알려드릴지 모르겠어요. 입력을 다시 확인해주세요!\n/remind [날짜] [리마인드할문자열]\n또는\n리마인드할 메세지에 답장후 /remind [날짜]"
                    )
                    return
            else:
                await message.reply_text("텍스트를 찾을 수 없어요!")
                return
        else:
            if len(user_input) > 2:
                result = self.regist(
                    chat_id,
                    user_id,
                    user_input[2].strip(),
                    remind_text_id,
                    user_input[1].strip(),
                    "param",
                )
                await message.reply_text(result["message"])
            else:
                await message.reply_text(
                    "다시 알려드릴 시간이나 메세지를 못찾겠어요. 입력을 다시 확인해주세요!\n/remind [날짜] [리마인드할문자열]\n또는\n리마인드할 메세지에 답장후 /remind [날짜]"
                )
                return

        def _write():
            with open(file_path, "w") as outfile:
                json.dump(self.alert_users, outfile, indent=4, ensure_ascii=False)

        await asyncio.get_running_loop().run_in_executor(None, _write)

    async def reminder_delete_command(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        if message.from_user is None:
            return
        user_id = message.from_user.id
        chat_id = message.chat.id
        registered_work = [
            [
                KeyboardButton(
                    text="{}\n\n{}".format(item["remind_text"], item["remind_uuid"])
                )
            ]
            for item in self.alert_users
            if item["reminder_user_id"] == user_id
        ]
        if len(registered_work) == 0:
            await self.bot.send_message(chat_id=chat_id, text="삭제할 리마인더가 없어요!")
            return ConversationHandler.END
        registered_work.append([KeyboardButton(text="선택종료")])
        await message.reply_text(
            "취소할 리마인더를 선택해주세요!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=registered_work, resize_keyboard=True, selective=True
            ),
        )
        return DREMIND

    async def remind_delete_error(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        #    with open(file_path, 'w') as outfile:
        #        json.dump(self.alert_users, outfile, indent=4, ensure_ascii=False)
        #        await self.bot.send_message(message.chat.id, '해제했어요!')
        await message.reply_text(
            "에러 또는 선생님의 선택으로 취소됐어요!", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def remind_delete(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ):
        token = (message.text or "").split("\n")
        if token[0] == "선택종료":
            await message.reply_text(
                "리마인더 선택 끝! 삭제할게요!", reply_markup=ReplyKeyboardRemove()
            )
            with open(file_path, "w") as outfile:
                json.dump(self.alert_users, outfile, indent=4, ensure_ascii=False)
                await message.reply_text("삭제처리 끝!")
                return ConversationHandler.END
        else:
            for remind_task in self.alert_users[:]:
                if token[2] == remind_task["remind_uuid"]:
                    await self.bot.send_message(
                        chat_id=remind_task["remind_chat_id"],
                        text=f'리마인더 {remind_task["remind_text"]}를 선택했어요!',
                    )
                    self.alert_users.remove(remind_task)
            return DREMIND

    def regist(self, chat_id, user_id, remind_text, remind_text_id, user_date, type):
        result = self.is_correct_time(user_date)

        if result["result"]:
            self.alert_users.append(
                {
                    "remind_date": result["date"],
                    "remind_chat_id": chat_id,
                    "remind_input_type": type,
                    "reminder_user_id": user_id,
                    "remind_message_id": remind_text_id,
                    "remind_text": remind_text,
                    "remind_uuid": str(uuid.uuid4()),
                }
            )
            self.alert_users.sort(key=lambda alert_user: alert_user["remind_text"])

        return result

    def is_correct_time(self, user_date):
        default_date = datetime.datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d")
        is_correct = {}
        fin_date = default_date + user_date if len(user_date) == 4 else user_date
        if is_only_time.match(user_date):
            is_correct["result"] = True
            is_correct["date"] = fin_date
            is_correct["message"] = "{}에 다시 알려드릴게요!".format(
                datetime.datetime.strptime(fin_date, "%Y%m%d%H%M")
            )
        else:
            is_correct["result"] = False
            is_correct[
                "message"
            ] = "저런, 날짜형식에 맞지 않는것같아요! 아래 예시를 참고해주세요!\nYYYYmmddHHMM(예시: 202107071800)\n또는\nHHMM(예시: 1800)"

        return is_correct
