import json
import os
from pathlib import Path

from app.database.database import SessionManager
from app.database.models import Message


class LoadMsg:
    def __init__(self) -> None:
        self.path = self.get_file_path()

    def get_file_path(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        return base_dir / "fixtures/messages.json"

    def is_valid_path(self):
        return os.path.exists(self.path)

    def read_file(self):
        with open(self.path, "r") as json_file:
            return json.load(json_file)

    def create_msg(self, data):
        return Message(
            text=data["text"],
            key=data["key"],
            keys=data["keys"],
            keys_per_row=data["keys_per_row"]
        )

    def load_msg(self, messages):
        with SessionManager() as db:
            db.query(Message).delete()
            db.commit()
            for data in messages:
                msg = self.create_msg(data)
                db.add(msg)
                db.commit()

    def run(self):
        if not self.is_valid_path():
            exit(f"File: {self.path} not found")

        msgs = self.read_file()
        self.load_msg(msgs)