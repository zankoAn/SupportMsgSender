from sqlalchemy.exc import IntegrityError

from app.database.database import SessionManager
from app.database.models import User, Message, GmailAccount, Order
from sqlalchemy import desc, update


class UserManager:
    def get_or_create(self, **user_params):
        user = self.get_user(chat_id=user_params.get("chat_id"))
        if not user:
            user = User(**user_params)
            with SessionManager() as db:
                try:
                    db.add(user)
                    db.commit()
                    db.refresh(user)
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

    def get_emails(self, limit):
        with SessionManager() as db:
            try:
                gmails = db.query(GmailAccount).limit(limit).all()
                return gmails
            except IntegrityError:
                db.rollback()


class OrderManager:
    def create(self, user_id, count):
        order = Order(user_id=user_id, count=count)
        with SessionManager() as db:
            try:
                db.add(order)
                db.commit()
            except IntegrityError:
                db.rollback()

    def update(self, user_id, **update_data):
        with SessionManager() as db:
            try:
                update_statement = (
                    update(Order)
                    .where(Order.id==db.query(Order.id).filter(user_id==user_id).order_by(desc(Order.id)).limit(1).scalar())
                    .values(update_data)
                )
                db.execute(update_statement)
                db.commit()
            except IntegrityError:
                db.rollback()

    def get_last_order(self, user_id):
        with SessionManager() as db:
            try:
                order = db.query(Order).filter(user_id==user_id).order_by(desc(Order.id)).limit(1).scalar()
                return order
            except IntegrityError:
                db.rollback()