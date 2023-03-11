import asyncio
import json
import os.path
import textwrap
from typing import Any, Dict, List, Mapping, Optional, Union

import httpx
from telegram import Bot, Message, Update
from telegram.ext import ContextTypes

from chiyakbot.utils import privileged_message

from . import AbstractChatbotModel, BaseAnswerMachine, CommandAnswerMachine, escape

file_path = "./registerd.json"


class AppleStorePickupModel(AbstractChatbotModel):
    watch_task: Optional[asyncio.Task]
    alert_users: Dict[str, List]
    name = "Apple Store Pickup Check"

    def __init__(self, bot: Bot, owner_id: str) -> None:
        super().__init__(bot, owner_id)

        self.watch_task = None
        self.alert_users = {}
        if os.path.exists(file_path):
            with open(file_path, "r") as json_file:
                self.alert_users = json.load(json_file)

    def list_available_handlers(self) -> List[BaseAnswerMachine]:
        return [
            CommandAnswerMachine(self.check_pickup_handler, "cp"),
            CommandAnswerMachine(self.watch_pickup_status, "cpl"),
            CommandAnswerMachine(self.delete_watching_item, "cpd"),
            CommandAnswerMachine(self.register_watching_item, "cpr"),
        ]

    async def check_pickup_handler(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        assert update.message is not None
        is_correct = (update.message.text or "").split(" ")
        length = len(is_correct)
        result = {}
        print(is_correct)
        if length <= 1:
            result = await self.check_pickup("MHR43KH/A")
        else:
            model = is_correct[1].strip()
            result = await self.check_pickup(model)

        if isinstance(result, str):
            await update.message.reply_text(result, parse_mode="MarkdownV2")
            return
        else:
            res = textwrap.dedent(
                """
                    이름 : {0}
                    가격 : {1}
                    학생가격 : {2}
                    구매 : {3}
                    픽업 : {4}
                    픽업가능스토어 : {5}
                    [*학생구매링크*]({6})"""
            ).format(
                result["name"],
                result["price"],
                result["univPrice"],
                result["isBuyable"],
                result["isPickable"],
                result["pickableStore"],
                result["link"],
            )
            await update.message.reply_text(res, parse_mode="MarkdownV2")

    async def pickup_watching_task(self, _type: str) -> None:
        while True:
            for model in self.alert_users.keys():
                if await self.is_item_available(model, _type):
                    for chatid in self.alert_users[model]:
                        result = await self.check_pickup(model)
                        if isinstance(result, str):
                            continue
                        res = textwrap.dedent(
                            """
                                이름 : {0}
                                가격 : {1}
                                학생가격 : {2}
                                구매 : {3}
                                픽업 : {4}
                                픽업가능스토어 : {5}
                                [*학생구매링크*]({6})"""
                        ).format(
                            result["name"],
                            result["price"],
                            result["univPrice"],
                            result["isBuyable"],
                            result["isPickable"],
                            result["pickableStore"],
                            result["link"],
                        )
                        await self.bot.send_message(
                            chat_id=chatid, text=res, parse_mode="MarkdownV2"
                        )
                        await self.bot.send_message(
                            chat_id=chatid, text=res, parse_mode="MarkdownV2"
                        )
                        await self.bot.send_message(
                            chat_id=chatid, text=res, parse_mode="MarkdownV2"
                        )
                    del self.alert_users[model][0:]

            def _write():
                with open(file_path, "w") as outfile:
                    emptylist = list(self.alert_users.keys())
                    for model in emptylist:
                        if len(self.alert_users[model]) == 0:
                            del self.alert_users[model]
                    json.dump(self.alert_users, outfile, indent=4)

            await asyncio.get_running_loop().run_in_executor(None, _write)
            await asyncio.sleep(60)

    @privileged_message
    async def watch_pickup_status(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await self.bot.send_message(message.chat.id, "감시시작!")
        _type = (message.text or "").split(" ")
        if self.watch_task:
            self.watch_task.cancel()
            await self.watch_task
        self.watch_task = asyncio.create_task(
            self.pickup_watching_task("pickup" if len(_type) <= 1 else _type[1])
        )

    async def register_watching_item(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        is_correct = (message.text or "").split(" ", 1)
        print(is_correct, message.chat.id)
        if len(is_correct) <= 1:
            if "MHR43KH/A" not in self.alert_users:
                self.alert_users["MHR43KH/A"] = []
            self.alert_users["MHR43KH/A"].append(message.chat.id)
        else:
            key = is_correct[1].strip()
            if key not in self.alert_users:
                self.alert_users[key] = []
            self.alert_users[key].append(message.chat.id)

        def _write():
            with open(file_path, "w") as outfile:
                json.dump(self.alert_users, outfile, indent=4)

        await asyncio.get_running_loop().run_in_executor(None, _write)
        await self.bot.send_message(message.chat.id, "등록했어요!")

    async def delete_watching_item(
        self, update: Update, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        is_correct = (message.text or "").split(" ", 1)
        if len(is_correct) <= 1:
            if "MHR43KH/A" not in self.alert_users:
                await self.bot.send_message(message.chat.id, "예약하신 적이 없어요!")
                return
            self.alert_users["MHR43KH/A"].remove(message.chat.id)
            if len(self.alert_users["MHR43KH/A"]) == 0:
                del self.alert_users["MHR43KH/A"]
        else:
            model = is_correct[1].strip()
            if model not in self.alert_users:
                await self.bot.send_message(message.chat.id, "예약하신 적이 없어요!")
                return
            self.alert_users[model].remove(message.chat.id)
            if len(self.alert_users[model]) == 0:
                del self.alert_users[model]

        def _write():
            with open(file_path, "w") as outfile:
                json.dump(self.alert_users, outfile, indent=4)

        await asyncio.get_running_loop().run_in_executor(None, _write)
        await self.bot.send_message(message.chat.id, "해제했어요!")

    async def check_pickup(self, model: str) -> Union[str, Mapping]:
        check_pickup_url = "https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}".format(
            model
        )
        check_available_stores_url = "https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}&location=06028".format(
            model
        )

        name_url = f"https://www.apple.com/kr/shop/configUpdate/{model}"
        k12_price_url = f"https://www.apple.com/kr-k12/shop/configUpdate/{model}"
        base_buy_url = "https://www.apple.com/kr/shop/product/"
        base_k12_buy_url = "https://www.apple.com/kr-k12/shop/product/"

        async with httpx.AsyncClient() as client:
            resp = await client.get(check_pickup_url)
            pickup_status = resp.json()
            resp = await client.get(name_url)
            model_name_json = resp.json()
            resp = await client.get(k12_price_url)
            k12_price = resp.json()

        result = {}
        if (
            pickup_status["head"]["status"] == "200"
            and "body" in pickup_status
            and "body" in model_name_json
        ):
            model_pickup_status = pickup_status["body"]["content"]["pickupMessage"][
                "pickupEligibility"
            ][model]
            model_info = model_name_json["body"]["replace"]["summary"]
            k12_price_info = k12_price["body"]["replace"]["summary"]
            purchasable = pickup_status["body"]["content"]["deliveryMessage"][model][
                "purchasable"
            ]
            product_name = escape.escape_for_md(model_info["displayName"], True)

            try:
                result["name"] = (
                    "[*" + product_name + "*]({0})".format(base_buy_url + model)
                )
                if model_pickup_status["storePickEligible"]:
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(check_available_stores_url)
                        store_info = resp.json()

                    store = store_info["body"]["content"]["pickupMessage"]["stores"]
                    available_store = []
                    if store[0]["partsAvailability"][model]["storeSelectionEnabled"]:
                        available_store.append("가로수길")
                    if store[1]["partsAvailability"][model]["storeSelectionEnabled"]:
                        available_store.append("여의도")
                    result["isPickable"] = "씹가능" if available_store != [] else "불가능"
                    result["pickableStore"] = (
                        available_store if available_store != [] else "재고없음"
                    )
                else:
                    result["isPickable"] = "불가능"
                    result["pickableStore"] = "없음"
                result["purchasable"] = "씹가능" if purchasable else "불가능"
                result["price"] = model_info["prices"]["total"]
                result["univPrice"] = k12_price_info["prices"]["total"]
                result["link"] = base_k12_buy_url + model
                return result
            except Exception as e:
                print(e)
                return "몬가이상함\\(exception\\)"
        else:
            return "팀쿡이 안알랴줌\\(no response body\\)"

    async def is_item_available(self, model: str, _type: Any) -> bool:
        check_pickup_url = "https://www.apple.com/kr/shop/fulfillment-messages?little=false&mt=regular&parts.0={0}".format(
            model
        )
        async with httpx.AsyncClient() as client:
            resp = await client.get(check_pickup_url)
            data = resp.json()
        result = (
            data["body"]["content"]["pickupMessage"]["pickupEligibility"][model][
                "storePickEligible"
            ]
            if _type == "pickup"
            else data["body"]["content"]["deliveryMessage"][model]["isBuyable"]
        )
        return result
