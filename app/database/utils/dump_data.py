import json
from pathlib import Path

from app.database.database import SessionManager
from app.database.models import Message


class DumpMsg:
    def __init__(self) -> None:
        self.path = self.get_file_path()

    def get_file_path(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        return base_dir / "fixtures/messages.json"

    def read_db_msg(self):
        with SessionManager() as db:
            messages = db.query(Message).all()
        return [
            {
                "text": msg.text,
                "key": msg.key,
                "keys": msg.keys,
                "keys_per_row": msg.keys_per_row
            } for msg in messages
        ]

    def dump_msg_to_file(self, data):
        with open(self.path, "w") as json_file:
            json.dump(data, json_file, indent=2)

    def run(self):
        data = self.read_db_msg()
        self.dump_msg_to_file(data)