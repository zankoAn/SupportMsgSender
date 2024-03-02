import json
import requests

from app.utils.load_env import config
from app.telegram.schemas import SendMessageSerializer


class Telegram:
    WEBHOOK_URL= "https://api.telegram.org/bot{}/{}"
    HEADERS = {"Cache-Control": "no-cache"}
    PROXY = []

    def __init__(self):
        if config.PROXY_SOCKS:
            self.PROXY = {
                "http": f'socks5h://{config.PROXY_SOCKS}',
                "https": f'socks5h://{config.PROXY_SOCKS}'
            }

    def bot(self, telegram_method: str, data: dict, method: str = "GET", input_file=None, params: dict={}) -> dict:
        url = self.WEBHOOK_URL.format(config.TOKEN, telegram_method)
        try:
            if method == "GET":
                response = requests.get(
                    url=url,
                    params=data,
                    proxies=self.PROXY,
                    headers=self.HEADERS
                )
            else:
                response = requests.post(
                    url=url,
                    data=data,
                    params=params,
                    files=input_file,
                    timeout=100,
                    proxies=self.proxy,
                    headers=self.HEADERS
                )
            response_data = json.loads(response.text) if response.text else {}
            return response_data
        except Exception as error:
            print("Error in Telegram Class: ", error)
            return {}

    def send_message(self, data: SendMessageSerializer):
        data = data.dict()
        result = self.bot(telegram_method="sendMessage", data=data)
        return result