import asyncio
import aiohttp
import random
import time
from colorama import Fore, init
from src.core.base_module import BaseModule

init(autoreset=True)

class HeartbeatGen(BaseModule):
    name = "HeartbeatGen"

    def __init__(self):
        super().__init__()
        self.sites = ["https://www.google.com", "https://www.wikipedia.org", "https://www.github.com"]

    def banner(self):
        print(f"{Fore.CYAN}HeartbeatGen - Traffic Simulation")

    async def _send_request(self, session):
        site = random.choice(self.sites)
        try:
            async with session.get(site, timeout=2) as response:
                print(f"{Fore.GREEN}[*] Heartbeat to {site}: {response.status}")
        except Exception:
            pass

    async def run_heartbeat(self, count):
        async with aiohttp.ClientSession() as session:
            for _ in range(count):
                await self._send_request(session)
                await asyncio.sleep(random.uniform(1, 5))

    def run(self):
        self.banner()
        count = int(input(f"{Fore.GREEN}[?] Number of heartbeats: "))
        print(f"{Fore.WHITE}[*] Starting traffic simulation...")
        asyncio.run(self.run_heartbeat(count))
        print(f"{Fore.CYAN}[*] Simulation done.")
        self.pause()
