import asyncio
import random

from pathlib import Path
from aiohttp import ClientSession
from aiohttp_socks import ProxyType, ProxyConnector
from bs4 import BeautifulSoup


class SendSupportTicket:
    BASE_PATH = Path(__file__).resolve().parent.parent

    def __init__(self) -> None:
        self.base_url = "https://telegram.org/support"
        self.base_data = {
            "message": None,
            "email": None,
            "phone": None,
            "setln": None,
        }
        self.base_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://telegram.org",
            "Referer": "https://telegram.org/support",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def get_proxy(self):
        file_path = self.BASE_PATH / "tmp/proxies.txt"
        with open(file_path) as p_file:
            proxies = p_file.read().split("\n")
        return random.choice(proxies)

    async def get_messages(self):
        file_path = self.BASE_PATH / "tmp/ticket_msg.txt"
        with open(file_path) as m_file:
            msgs = m_file.read().split("\n")
        return random.choice(msgs)

    async def get_connector(self, proxy: str):
        host, port, user, password = proxy
        connector = ProxyConnector(
            proxy_type=ProxyType.SOCKS5,
            host=host,
            port=port,
            username=user,
            password=password,
            rdns=True
        )
        return connector

    async def send_msg(self, session, msg, email, phone):
        self.base_data.update({"message": msg, "email": email, "phone": phone})
        async with session.post(url=self.base_url, data=self.base_data, headers=self.base_headers) as resp:
            data = await resp.text()
            return data

    async def extract_success_alert(self, data):
        soup = BeautifulSoup(data, "html.parser")
        support_wrap = soup.find(class_="support_wrap")
        if support_wrap:
            alert = support_wrap.find(class_="alert")
            if alert:
                return alert.text.strip()
        return None

    async def run(self, email, phone):
        proxy = (await self.get_proxy()).split(":")
        msg = await self.get_messages()
        connector = await self.get_connector(proxy)
        async with ClientSession(connector=connector) as session:
            data = await self.send_msg(session, msg, email, phone)
            success_alert = await self.extract_success_alert(data)
            print(success_alert)
            return success_alert


async def main():
    ticket = SendSupportTicket()
    await ticket.run("test", "test@gmail.com", "")


if __name__ == "__main__":
    asyncio.run(main())