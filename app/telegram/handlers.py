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
from app.database.models import UserRoleEnum, OrderStatusEnum



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

    def is_superuser(self):
        if self.user.role == UserRoleEnum.admin:
            return True

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

    async def handler(self):
        text_msg = None
        if self.update.message.text:
            text_msg = MessageManager().get_related_msg(key=self.update.message.text)

        if text_msg:
            UserManager().update(self.user.chat_id, step=text_msg.current_step)
            return await UserTextHandler(self).run(text_msg)
        else:
            return await UserStepHandler(self).run()

    async def run(self):
        self.add_new_user()
        if not self.is_superuser(): return
        await self.handler()

class UserTextHandler(BaseHandler):

    def __init__(self, base):
        for key, value in vars(base).items():
            setattr(self, key, value)

    async def home_page(self, msg):
        msg = MessageManager().get_related_msg(current_step=msg.current_step)
        return msg

    async def handler(self, msg):
        chat_id = self.update.message.chat.id
        if update_text_method := getattr(self, msg.current_step, None):
            msg = await update_text_method(msg)

        key = self.generate_keyboards(msg)
        serialized_data = SendMessageSerializer(chat_id=chat_id, text=msg.text, reply_markup=key)
        self.bot.send_message(serialized_data)

    async def run(self, text_msg):
        await self.handler(text_msg)


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

    async def get_ticket_msg(self) -> None:
        base_path = Path(__file__).resolve().parent.parent
        file_path = base_path / "tmp/ticket_msg.txt"
        self.save_file_contents(file_path)
        self.send_success_message("add_data_success")

    async def get_proxies(self) -> None:
        if not self.update.message.document:
            try:
                host, port, ip, passwd = self.update.message.text.split(":")
            except ValueError as error:
                print(error)
                return self.handle_exception(error)

        base_path = Path(__file__).resolve().parent.parent
        file_path = base_path / "tmp/proxies.txt"
        self.save_file_contents(file_path)
        self.send_success_message("add_data_success")

    async def get_order_send_count(self) -> None:
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

    async def get_order_sleep_time(self) -> None:
        try:
            text = self.update.message.text
            start, end = map(int, text.split("-"))
            if start > end:
                raise ValueError("Start time range must be smaller then end time range")
        except ValueError as error:
            return self.handle_exception(error)

        await TicketProcessingHandler(self).run()

    async def handler(self) -> None:
        if callback := self.steps.get(self.user.step):
            await callback()

    async def run(self) -> None:
        await self.handler()


class TicketProcessingHandler(BaseHandler):
    START_STEP_MSG = "start_send_ticket_msg"
    COMPLETION_STEP_MSG = "completion_send_ticket_msg"

    def __init__(self, base) -> None:
        for key, value in vars(base).items():
            setattr(self, key, value)
        self.chat_id = self.update.message.chat.id

    def update_order_and_user_step(self) -> None:
        text = self.update.message.text
        OrderManager().update(self.chat_id, sleep_range=text, status=OrderStatusEnum.PROCESSING)
        UserManager().update(self.chat_id, step="home_page")

    def get_order_and_emails(self) -> Tuple[OrderManager, GmailAccountManager]:
        last_order = OrderManager().get_last_order(self.chat_id)
        email_phones = GmailAccountManager().get_emails(limit=last_order.count)
        return last_order, email_phones

    def send_update_order_status_msg(self, counter=0, email_count=0, sleep_time=0, edit_msg_id=0) -> int:
        msg = MessageManager().get_related_msg(current_step=self.START_STEP_MSG)
        text_msg=msg.text.format(
            counter=counter,
            sleep_time=sleep_time,
            email_count=email_count
        )
        if edit_msg_id:
            serialized_data = EditMessageTextSerializer(
                chat_id=self.chat_id,
                message_id=edit_msg_id,
                text=text_msg
            )
            self.bot.edit_message_text(serialized_data)
        else:
            text_msg = SendMessageSerializer(
                chat_id=self.chat_id,
                text=text_msg
            )
            resp = self.bot.send_message(text_msg)
            return resp["result"]["message_id"]

    def send_completion_message(self, success_counter) -> None:
        msg = MessageManager().get_related_msg(current_step=self.COMPLETION_STEP_MSG)
        text_msg = SendMessageSerializer(
            chat_id=self.chat_id,
            text=msg.text.format(send_count=success_counter)
        )
        self.bot.send_message(text_msg)

    async def process_tickets(self, email_phones, last_order) -> None:
        start, end = last_order.sleep_range.split("-")
        success_counter = 0
        ticket = SendSupportTicket()
        msg_id = self.send_update_order_status_msg()
        try:
            for obj in email_phones:
                response= await ticket.run(email=obj.email, phone=obj.phone)
                if response and "Thanks for your report!" in response:
                    success_counter += 1

                sleep_time = random.randrange(int(start), int(end))
                self.send_update_order_status_msg(success_counter, len(email_phones), sleep_time, msg_id)
                await asyncio.sleep(sleep_time)

            OrderManager().update(self.chat_id, status=OrderStatusEnum.COMPLETED)
            self.send_completion_message(success_counter)
        except Exception as error:
            self.handle_exception(error)

    async def run(self) -> None:
        self.update_order_and_user_step()
        order, emails = self.get_order_and_emails()
        await self.process_tickets(emails, order)