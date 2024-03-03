from .database import SessionManager
from .models import User, Message

from sqlalchemy.exc import IntegrityError
from typing import List


class UserManager:
    def create(self, chat_id: int, username: str, step: str="home_page"):
        user = User(chat_id=chat_id, username=username, step=step)
        with SessionManager() as db:
            try:
                db.add(user)
                db.commit()
                db.refresh()
            except IntegrityError:
                db.rollback()
        return user


class MessageManager:
    def get_related_step_msg(self, step: str) -> Message | List[None]:
        with SessionManager() as db:
            msg = db.query(Message).filter_by(current_step=step).first()
        return msg

    def get_related_key_msg(self, update_key: str) -> Message | List[None]:
        with SessionManager() as db:
            msg = db.query(Message).filter_by(key=update_key).first()
        return msg