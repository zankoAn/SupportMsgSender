import uvicorn
import argparse

from pathlib import Path
from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError

from app.database.utils.dump_data import DumpMsg
from app.database.utils.load_data import LoadMsg
from app.utils.load_env import config

from app.database.crud import UserManager
from app.database.models import UserRoleEnum


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

    def promote_or_create_superuser(self, user_id, new_role):
        updated_count = UserManager().update(user_id, role=new_role)
        if not updated_count:
            UserManager().get_or_create(chat_id=user_id, role=new_role)
            print("User created with role:", new_role)
        else:
            print("User role successfully updated")

    def run(self):
        parser = argparse.ArgumentParser(description="Command-line Manager")
        subparsers = parser.add_subparsers(dest="action", help="Choose an action to perform")

        subparsers.add_parser("runserver", help="Start uvicorn webserver")
        subparsers.add_parser("makemigrations", help="Create new migration for changes")
        subparsers.add_parser("migrate", help="Apply migrations to update the database")
        subparsers.add_parser("loadmsg", help="Load fixtures data to the database")
        subparsers.add_parser("dumpmsg", help="Dump messages model into the fixture directory")

        promote_user = subparsers.add_parser("promote", help="Add or promote user to superuser")
        promote_user.add_argument("user_id", help="User ID", type=int)
        promote_user.add_argument("role", help="User role", choices=[role.value for role in UserRoleEnum])

        args = parser.parse_args()
        match args.action:
            case None:
                print("No subcommand provided. Please use 'python manage.py help' for assistance.")
            case "runserver":
                self.runserver()
            case "makemigrations":
                self.makemigrations()
            case "migrate":
                self.migrate()
            case "loadmsg":
                self.loadmsg()
            case "dumpmsg":
                self.dumpmsg()
            case "promote":
                user_id = args.user_id
                role = args.role
                self.promote_or_create_superuser(user_id, role)

if __name__ == "__main__":
    Manage().run()