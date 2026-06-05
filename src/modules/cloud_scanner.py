import asyncio
import aiohttp
from colorama import Fore, init
from src.core.base_module import BaseModule

init(autoreset=True)

class CloudScanner(BaseModule):
    name = "CloudScanner"

    def __init__(self):
        super().__init__()
        self.wordlist = ["backup", "data", "test", "files", "config", "public"]

    def banner(self):
        print(f"{Fore.CYAN}CloudScanner - Asynchronous S3 Bucket Enumeration")

    async def _check_bucket(self, session, bucket_name):
        url = f"https://{bucket_name}.s3.amazonaws.com"
        try:
            async with session.get(url, timeout=2) as response:
                if response.status == 200:
                    print(f"{Fore.GREEN}[+] Found Open Bucket: {url}")
                elif response.status == 403:
                    print(f"{Fore.YELLOW}[!] Bucket exists (Forbidden): {url}")
        except Exception:
            pass

    async def run_scan(self, base_name):
        async with aiohttp.ClientSession() as session:
            tasks = [self._check_bucket(session, f"{base_name}-{word}") for word in self.wordlist]
            await asyncio.gather(*tasks)

    def run(self):
        self.banner()
        target = input(f"{Fore.GREEN}[?] Base Name (e.g., target-company): ")
        print(f"{Fore.WHITE}[*] Starting S3 enumeration...")
        asyncio.run(self.run_scan(target))
        print(f"{Fore.CYAN}[*] Scan done.")
        self.pause()
