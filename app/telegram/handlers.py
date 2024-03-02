from app.telegram.bot import Telegram
from app.telegram.schemas import (
    UpdateSerializer, ReplyMarkupSerializer, KeyboardButtonSerializer,
    SendMessageSerializer
)
from app.database.crud import MessageManager



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

    def handler(self):
        text_msg = MessageManager().get_related_key_msg(self.update.message.text)
        if text_msg:
            return UserTextHandler(self).run(text_msg)
        else:
            #TODO StepHandler
            ...

    def run(self):
        self.handler()


class UserTextHandler(BaseHandler):

    def __init__(self, base):
        for key, value in vars(base).items():
            setattr(self, key, value)

    def show_status(self):
        ...

    def ask_ticket_msg_file(self):
        ...

    def ask_ticket_msg_data(self):
        ...

    def ask_account_file(self):
        ...

    def ask_account_data(self):
        ...

    def send_ticket_msg(self):
        ...

    def handler(self, msg):
        key = self.generate_keyboards(msg)
        serialized_data = SendMessageSerializer(
            chat_id=self.update.message.chat.id,
            text=msg.text,
            reply_markup=key
        )
        self.bot.send_message(serialized_data)

    def run(self, text_msg):
        self.handler(text_msg)


class UserStepHandler:

    def get_account_email(self):
        ...

    def get_account_password(self):
        ...

    def get_account_phone(self):
        ...

    def get_ticket_msg(self):
        ...

    def get_send_count(self):
        ...