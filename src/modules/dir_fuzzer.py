import asyncio
import aiohttp
from colorama import Fore, init
from src.core.base_module import BaseModule

init(autoreset=True)

class DirFuzzer(BaseModule):
    name = "DirFuzzer"

    def __init__(self):
        super().__init__()
        self.wordlist = ["admin", "config", "backup", "login", "uploads", "api", ".git", ".env"]

    def banner(self):
        print(f"{Fore.CYAN}DirFuzzer - Asynchronous Directory Discovery")

    async def _check_path(self, session, url, path):
        target = f"{url.rstrip('/')}/{path}"
        try:
            async with session.get(target, timeout=2) as response:
                print(f"DEBUG: Response status {response.status}")
                if response.status in [200, 301, 302, 403]:
                    print(f"{Fore.GREEN}[+] Found: {target} ({response.status})")
        except Exception as e:
            print(f"DEBUG: Exception {e}")
            pass

    async def run_fuzz(self, url):
        async with aiohttp.ClientSession() as session:
            tasks = [self._check_path(session, url, path) for path in self.wordlist]
            await asyncio.gather(*tasks)

    def run(self):
        self.banner()
        target = input(f"{Fore.GREEN}[?] Base URL (e.g., http://target.com): ")
        print(f"{Fore.WHITE}[*] Starting fuzz...")
        asyncio.run(self.run_fuzz(target))
        print(f"{Fore.CYAN}[*] Done.")
        self.pause()
