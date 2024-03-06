import random
import asyncio

from pathlib import Path
from typing import Tuple, List, Dict

from app.database.crud import (
    GmailAccountManager,
    MessageManager,
    OrderManager,
    UserManager
)
from app.telegram.bot import Telegram
from app.telegram.schemas import (
    KeyboardButtonSerializer,
    ReplyMarkupSerializer,
    SendMessageSerializer,
    EditMessageTextSerializer,
    UpdateSerializer
)
from app.utils.support_ticket import SendSupportTicket
from app.database.models import OrderStatusEnum



class BaseHandler:

    def __init__(self, update: UpdateSerializer) -> None:
        self.update = update
        self.user = None
        self.bot = Telegram()

    def generate_keyboards(self, msg):
        keys = msg.keys.split("\n")
        keyboard = [
            [KeyboardButtonSerializer(text=key) for key in keys[index: index + msg.keys_per_row]]
            for index in range(0, len(keys), msg.keys_per_row)
        ]
        return ReplyMarkupSerializer(
            keyboard = keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

    def add_new_user(self):
        msg = self.update.message
        self.user = UserManager().get_or_create(
            chat_id=msg.chat.id,
            username=msg.chat.username,
            first_name=msg.chat.first_name,
            last_name=msg.chat.last_name,
        )

    def handle_exception(self, error):
        tb = error.__traceback__
        file_name = tb.tb_frame.f_code.co_filename
        line_number = tb.tb_lineno
        msg = MessageManager().get_related_msg(current_step="error_msg")
        msg = SendMessageSerializer(
            chat_id=self.user.chat_id,
            text=msg.text.format(error=error, file_name=file_name, line_number=line_number)
        )
        self.bot.send_message(msg)

    def handler(self):
        text_msg = MessageManager().get_related_msg(key=self.update.message.text)
        if text_msg:
            UserManager().update(self.user.chat_id, step=text_msg.current_step)
            return UserTextHandler(self).run(text_msg)
        else:
            return UserStepHandler(self).run()

    def run(self):
        self.add_new_user()
        self.handler()


class UserTextHandler(BaseHandler):

    def __init__(self, base):
        for key, value in vars(base).items():
            setattr(self, key, value)

    def home_page(self, msg):
        msg = MessageManager().get_related_msg(current_step=msg.current_step)
        return msg

    def handler(self, msg):
        chat_id = self.update.message.chat.id
        if update_text_method := getattr(self, msg.current_step, None):
            msg = update_text_method(msg)

        key = self.generate_keyboards(msg)
        serialized_data = SendMessageSerializer(chat_id=chat_id, text=msg.text, reply_markup=key)
        self.bot.send_message(serialized_data)

    def run(self, text_msg):
        self.handler(text_msg)


class UserStepHandler(BaseHandler):

    def __init__(self, base) -> None:
        self.steps = {
            "add_gmail_page": self.get_email_and_phone,
            "add_msg_page": self.get_ticket_msg,
            "add_proxy_page": self.get_proxies,
            "send_tg_msg": self.get_order_send_count,
            "get_order_sleep_time": self.get_order_sleep_time,
        }
        for key, value in vars(base).items():
            setattr(self, key, value)

    def process_user_email_phone_data(self) -> List[Dict]:
        accounts = []
        if self.update.message.document:
            file_id = self.update.message.document.file_id
            file = self.bot.get_file(file_id)
            user_data = file.iter_lines(decode_unicode=True)
        else:
            user_data = self.update.message.text.strip().split("\n")

        for line in user_data:
            try:
                email, phone = line.strip().split(":")
                data = {"user_id": self.user.id, "email": email, "phone": phone}
                accounts.append(data)
            except ValueError as error:
                self.handle_exception(error)
        return accounts

    def save_file_contents(self, output_file_path) -> None:
        if self.update.message.document:
            file_id = self.update.message.document.file_id
            file = self.bot.get_file(file_id)
            msgs = [line.decode() for line in file.iter_lines(decode_unicode=True)]
        else:
            msgs = self.update.message.text.strip().split("\n")

        with open(output_file_path, "w") as msg_file:
            msg_file.write("\n".join(msgs))

    def send_success_message(self, current_step) -> None:
        msg = MessageManager().get_related_msg(current_step=current_step)
        serialized_data = SendMessageSerializer(chat_id=self.user.chat_id, text=msg.text)
        self.bot.send_message(serialized_data)

    def get_email_and_phone(self) -> None:
        accounts = self.process_user_email_phone_data()
        if accounts:
            GmailAccountManager().create(accounts)
            self.send_success_message("add_data_success")

    def get_ticket_msg(self) -> None:
        base_path = Path(__file__).resolve().parent.parent
        file_path = base_path / "tmp/ticket_msg.txt"
        self.save_file_contents(file_path)
        self.send_success_message("add_data_success")

    def get_proxies(self) -> None:
        if not self.update.message.document:
            try:
                host, port, ip, passwd = self.update.message.text.split(":")
            except ValueError as error:
                print(error)
                return self.handle_exception(error)

        base_path = Path(__file__).resolve().parent.parent
        file_path = base_path / "tmp/proxies.txt"
        self.store_file_contents(file_path)
        self.send_success_message("add_data_success")

    def get_order_send_count(self) -> None:
        try:
            text = self.update.message.text
            order_count = int(text)
        except ValueError as error:
            self.handle_exception(error)
            return

        chat_id = self.user.chat_id
        OrderManager().create(chat_id, order_count)
        UserManager().update(chat_id, step="get_order_sleep_time")
        msg = MessageManager().get_related_msg(current_step="get_order_sleep_time")
        text_msg = SendMessageSerializer(chat_id=chat_id, text=msg.text)
        self.bot.send_message(text_msg)

    def get_order_sleep_time(self) -> None:
        try:
            text = self.update.message.text
            start, end = map(int, text.split("-"))
            if start > end:
                raise ValueError("Start time range must be smaller then end time range")
        except ValueError as error:
            return self.handle_exception(error)


    def handler(self) -> None:
        if callback := self.steps.get(self.user.step):
            callback()

    def run(self) -> None:
        self.handler()


