from enum import Enum
from typing import Optional
from dataclasses import dataclass



class ParseMode(Enum):
    HTML = "html"
    MARKDOWN = "markdown"


class ReplyMarkup(Enum):
    INLINE_KEYBOARD_MARKUP = "InlineKeyboardMarkup"
    REPLY_KEYBOARD_MARKUP = "ReplyKeyboardMarkup"
    REPLY_KEYBOARD_REMOVE = "ReplyKeyboardRemove"
    FORCE_REPLY = "ForceReply"


class Entity(Enum):
    MENTION = "mention"
    HASHTAG = "hashtag"
    COMMAND = "bot_command"
    URL = "url"
    BOLD = "bold"
    CODE = "code"
    SPOILER = "spoiler"
    BLOCKQUOTE = "blockquote"
    LINK = "text_link"


@dataclass
class UserType:
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    language_code: Optional[str]
    is_premium: Optional[bool]


@dataclass
class MessageEntityType:
    type: Entity
    offset: int
    length: int
    url: Optional[str]
    user: Optional[UserType]
    language: Optional[str]
    custom_emoji_id: Optional[str]