import enum

from sqlalchemy import Column, Integer, String, ForeignKey, INTEGER
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class BaseAttributes:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)


class UserRoleEnum(enum.Enum):
    admin = "admin"
    member = "member"


class User(Base, BaseAttributes):
    __tablename__ = "user"

    chat_id = Column(Integer, unique=True, index=True)
    username = Column(String(50))
    step = Column(String(60), default="home_page")


class GmailAccount(Base, BaseAttributes):
    __tablename__ = "gmail_account"

    user_id = Column(Integer, ForeignKey("user.id"))
    email = Column(String(120), unique=True, index=True)
    phone_number = Column(String(16))
    password_hash = Column(String(128))


class Message(Base, BaseAttributes):
    __tablename__ = "bot_message"

    text = Column(String(80))
    key = Column(String(200))
    keys = Column(String)
    keys_per_row = Column(INTEGER, default=2)
    current_step = Column(String(60), default="home_page")