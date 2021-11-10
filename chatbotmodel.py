import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, InlineQueryHandler
import sys, os
from dotenv import load_dotenv

load_dotenv(verbose=True)

class TelegramBot:
    def __init__(self, name, token):
        self.core = telegram.Bot(token)
        self.updater = Updater(token)
        self.id = os.getenv('ADMIN_TG_ID')
        self.name = name

    def sendMessage(self, id, text):
        self.core.sendMessage(chat_id=id, text=text)

    def stop(self):
        self.updater.start_polling()
        self.updater.dispatcher.stop()
        self.updater.job_queue.stop()
        self.updater.stop()


class chiyakbot(TelegramBot):
    def __init__(self):
        self.token = os.getenv('TG_TOKEN') if sys.argv[1] != 'develop' else os.getenv('TG_BETA_TOKEN')
        TelegramBot.__init__(self, '치약봇', self.token)
        self.updater.stop()

    def add_cmdhandler(self, cmd, func):
        self.updater.dispatcher.add_handler(CommandHandler(cmd, func))

    def add_callhandler(self, func):
        self.updater.dispatcher.add_handler(CallbackQueryHandler(func))

    def add_messagehandler(self, func):
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, func))
    
    def add_conversationHandler(self, conversationHandler):
        self.updater.dispatcher.add_handler(conversationHandler)
    
    def add_inlinequeryhandler(self, queryhandler):
        self.updater.dispatcher.add_handler(InlineQueryHandler(queryhandler))

    def start(self):
        self.sendMessage(self.id, '안녕하세요! 일어났어요.')
        self.updater.start_polling(timeout=5, drop_pending_updates=True)
        self.updater.idle()
