from app.telegram.bot import Telegram
from app.telegram.schemas import (
    UpdateSerializer, ReplyMarkupSerializer, KeyboardButtonSerializer,
    SendMessageSerializer
)
from app.database.crud import MessageManager, UserManager



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

    def handler(self):
        text_msg = MessageManager().get_related_msg(key=self.update.message.text)
        if text_msg:
            UserManager().update(self.user.chat_id, step=text_msg.current_step)
            return UserTextHandler(self).run(text_msg)
        else:
            #TODO StepHandler
            ...

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

    def show_status(self):
        ...

    def handler(self, msg):
        chat_id = self.update.message.chat.id
        if update_text_method := getattr(self, msg.current_step, None):
            msg = update_text_method(msg)

        key = self.generate_keyboards(msg)
        serialized_data = SendMessageSerializer(chat_id=chat_id, text=msg.text, reply_markup=key)
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