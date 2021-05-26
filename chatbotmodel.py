import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

class TelegramBot:
    def __init__(self, name, token):
        self.core = telegram.Bot(token)
        self.updater = Updater(token)
        self.id = 46674072
        self.name = name

    def sendMessage(self, id, text):
        self.core.sendMessage(chat_id = id, text = text)

    def stop(self):
        self.updater.start_polling()
        self.updater.dispatcher.stop()
        self.updater.job_queue.stop()
        self.updater.stop()

class chiyakbot(TelegramBot):
    def __init__(self):
        self.token = '584670337:AAEp9NMHIV-EpECLBbCMkWA0sBt17UmWkd8'
        TelegramBot.__init__(self, '치약봇', self.token)
        self.updater.stop()

    def add_cmdhandler(self, cmd, func):
        self.updater.dispatcher.add_handler(CommandHandler(cmd, func))

    def add_callhandler(self, func):
        self.updater.dispatcher.add_handler(CallbackQueryHandler(func))

    def add_messagehandler(self, func):
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, func))

    def start(self):
        self.sendMessage(self.id, '안녕하세요! 일어났어요.')
        self.updater.start_polling(timeout=5, drop_pending_updates=True)
        self.updater.idle()
