import configparser
from pathlib import Path


class Config:
    def __init__(self, env=".env") -> None:
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.load_config(env)

    def load_config(self, env):
        config = configparser.ConfigParser(interpolation=None)
        file_name = self.BASE_DIR / f"{env}.ini"
        config.read(file_name)
        for section_name in config.sections():
            for key, value in config[section_name].items():
                setattr(self, key.upper(), value)

config = Config()