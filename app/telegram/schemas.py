import json

from typing import Union, Optional, List

from pydantic import BaseModel, Field

from datetime import datetime

from app.telegram.types import ParseMode, MessageEntityType



class Base(BaseModel):
    class Config:
        extra = "allow"


class ChatSerializer(Base):
    id: int
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    username: Optional[str] = ""


class DocumentSerializer(Base):
    file_name: str
    mime_type: str
    file_id: str
    file_unique_id: str
    file_size: int


class MessageSerializer(Base):
    message_id: int
    chat: ChatSerializer
    text: Optional[str] = ""
    reply_to_message: Optional[dict] = ""
    from_user: ChatSerializer = Field(..., alias="from")
    document: Optional[DocumentSerializer] = None


class CallbackSerializer(Base):
    id: int
    data: str
    message: MessageSerializer


class UpdateSerializer(Base):
    message: Optional[MessageSerializer] = ""
    callback_query: Optional[CallbackSerializer] = ""


class KeyboardButtonSerializer(BaseModel):
    text: str
    request_contact: Optional[bool] = False
    request_location: Optional[bool] = False


class ReplyMarkupSerializer(BaseModel):
    keyboard: List[List[KeyboardButtonSerializer]]
    is_persistent: Optional[bool] = False
    resize_keyboard	: Optional[bool] = False
    one_time_keyboard: Optional[bool] = False


class SendMessageSerializer(BaseModel):
    chat_id: Union[int, str]
    text: str
    parse_mode: Optional[ParseMode] = ParseMode.HTML.value
    entities: Optional[List[MessageEntityType]] = None
    disable_web_page_preview: bool = True
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[int] = None
    schedule_date: Optional[datetime] = None
    protect_content: Optional[bool] = None
    reply_markup:Optional[ReplyMarkupSerializer] = None

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        if reply_markup := data.get("reply_markup"):
            data["reply_markup"] = json.dumps(reply_markup)
        return data
