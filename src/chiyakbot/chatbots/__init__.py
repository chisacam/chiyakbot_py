from typing import Any, Callable, Coroutine, Iterable, List, Optional, Type

from telegram import Bot, Message, Update
from telegram.ext import ContextTypes, ConversationHandler

AbstractHandlerType = Type[
    Callable[[Update, ContextTypes.DEFAULT_TYPE], Coroutine[Any, Any, None]]
]
MessageHandlerType = Type[
    Callable[[Update, Message, ContextTypes.DEFAULT_TYPE], Coroutine[Any, Any, None]]
]


class BaseAnswerMachine:
    handler: AbstractHandlerType
    description: Optional[str] = None

    def __init__(
        self, handler: AbstractHandlerType, description: Optional[str] = None
    ) -> None:
        self.handler = handler
        self.description = description

    @classmethod
    def message_handler_generator(
        cls, handler: MessageHandlerType
    ) -> AbstractHandlerType:
        async def _fn(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.message is None:
                return
            await handler(update, update.message, context)

        return _fn


class MessageAnswerMachine(BaseAnswerMachine):
    def __init__(
        self, handler: MessageHandlerType, description: Optional[str] = None
    ) -> None:
        super().__init__(self.message_handler_generator(handler), description)


class CommandAnswerMachine(MessageAnswerMachine):
    command: str

    def __init__(
        self,
        handler: MessageHandlerType,
        command: str,
        description: Optional[str] = None,
    ) -> None:
        super().__init__(handler, description)
        self.command = command

    def __str__(self) -> str:
        return f"CommandAnswerMachine(/{self.command})"

    def __repr__(self) -> str:
        return self.__str__()


class InlineQueryAnswerMachine(BaseAnswerMachine):
    pass


class AbstractChatbotModel:
    name: str
    bot: Bot
    owner_id: str

    def __init__(self, bot: Bot, owner_id: str) -> None:
        if not hasattr(self, "name"):
            self.name = ""
        self.bot = bot
        self.owner_id = owner_id

    def list_available_handlers(self) -> Iterable[BaseAnswerMachine]:
        raise NotImplementedError

    def list_available_conversations(self) -> Iterable[ConversationHandler]:
        return []


from .chatgpt import ChatGPTModel
from .doortodoor import DeliveryInfoModel
from .exchange import ExchangeModel
from .inko import InkoModel
from .message_detector import MessageDetectorModel
from .papago import PapagoModel
from .sauceNAO import SimilarImageModel
from .reminder import ReminderModel
from .deepl import DeeplModel
from .speller import SpellerModel
from .chzzk import ChzzkModel

defined_models: List = [
    ChatGPTModel,
    DeliveryInfoModel,
    ExchangeModel,
    MessageDetectorModel,
    PapagoModel,
    SimilarImageModel,
    InkoModel,
    ReminderModel,
    DeeplModel,
    SpellerModel,
    ChzzkModel,
]
