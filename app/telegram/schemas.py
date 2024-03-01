from pydantic import BaseModel, Field
from typing import Optional


class Base(BaseModel):
    class Config:
        extra = "allow"


class ChatSerializer(Base):
    id: int
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    username: Optional[str] = ""


class MessageSerializer(Base):
    message_id: int
    chat: ChatSerializer
    text: Optional[str] = ""
    reply_to_message: Optional[dict] = ""
    from_user: ChatSerializer = Field(..., alias="from")


class CallbackSerializer(Base):
    id: int
    data: str
    message: MessageSerializer


class UpdateSerializer(Base):
    message: Optional[MessageSerializer] = ""
    callback_query: Optional[CallbackSerializer] = ""