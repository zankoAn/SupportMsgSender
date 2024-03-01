import sys
import uvicorn

from pathlib import Path
from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError

from app.database.utils.dump_data import DumpMsg
from app.database.utils.load_data import LoadMsg
from app.utils.load_env import config


class Manage:
    BASE_DIR = Path(__file__).resolve().parent

    def __init__(self) -> None:
        self.alembic_cfg = Config(self.BASE_DIR / "alembic.ini")

    def runserver(self):
        is_reload = bool(config.RELOAD)
        uvicorn.run(
            app="app.main:app",
            host=config.HOST,
            port=int(config.PORT),
            reload=is_reload,
            workers=None if is_reload else int(config.WORKERS),
            log_level=config.LOGLEVEL if config.LOGLEVEL else None
        )

    def makemigrations(self):
        try:
            command.revision(self.alembic_cfg, autogenerate=True)
        except CommandError:
            print("No changes detected")

    def migrate(self):
        command.upgrade(self.alembic_cfg, "head")

    def loadmsg(self):
        LoadMsg().run()
        print("Load data successfully.")

    def dumpmsg(self):
        DumpMsg().run()
        print("Dump data successfully.")

    def run(self, command: str):
        getattr(self, command)()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        Manage().run(sys.argv[1])