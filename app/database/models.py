import enum

from sqlalchemy import Column, Integer, String, ForeignKey, INTEGER, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class BaseAttributes:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)


class UserRoleEnum(enum.Enum):
    admin = "admin"
    member = "member"


class OrderStatusEnum(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CANCELED = "canceled"
    COMPLETED = "completed"


class User(Base, BaseAttributes):
    __tablename__ = "user"

    chat_id = Column(Integer, unique=True, index=True)
    username = Column(String(50), default="")
    first_name = Column(String(100), default="")
    last_name = Column(String(100), default="")
    step = Column(String(60), default="home_page")
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.member)


class GmailAccount(Base, BaseAttributes):
    __tablename__ = "gmail_account"

    user_id = Column(Integer, ForeignKey("user.id"))
    email = Column(String(120), unique=True, index=True)
    phone = Column(String(16))


class Message(Base, BaseAttributes):
    __tablename__ = "bot_message"

    text = Column(String(80))
    key = Column(String(200))
    keys = Column(String)
    keys_per_row = Column(INTEGER, default=2)
    current_step = Column(String(60), default="home_page")


class Order(Base, BaseAttributes):
    __tablename__ = "order"

    user_id = Column(Integer, ForeignKey("user.id"))
    count = Column(Integer)
    sleep_range = Column(String(15), default="1-3")
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING)
    created = Column(DateTime)