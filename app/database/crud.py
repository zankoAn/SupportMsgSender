from sqlalchemy.exc import IntegrityError

from app.database.database import SessionManager
from app.database.models import User, Message, GmailAccount
from app.telegram.types import UserType


class UserManager:
    def get_or_create(self, **user_params):
        user = self.get_user(chat_id=user_params.get("chat_id"))
        if not user:
            user = User(**user_params)
            with SessionManager() as db:
                try:
                    db.add(user)
                    db.commit()
                except IntegrityError:
                    db.rollback()
        return user

    def get_user(self, **criterion):
        try:
            with SessionManager() as db:
                user = db.query(User).filter_by(**criterion).first()
            return user
        except Exception as err:
            print(err)
            return None

    def update(self, user_id: int, **update_data):
        with SessionManager() as db:
            try:
                db.query(User).filter(User.chat_id==user_id).update(update_data)
                db.commit()
            except IntegrityError:
                db.rollback()


class MessageManager:
    def get_related_msg(self, **criterion) -> Message:
        try:
            with SessionManager() as db:
                msg = db.query(Message).filter_by(**criterion).first()
            return msg
        except Exception as err:
            print(err)


class GmailAccountManager:
    def create(self,  account_data_list):
        accounts = [GmailAccount(**data) for data in account_data_list]
        with SessionManager() as db:
            try:
                db.add_all(accounts)
                db.commit()
            except IntegrityError:
                db.rollback()
