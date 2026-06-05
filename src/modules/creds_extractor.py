import os
import re
from colorama import Fore, init
from src.core.base_module import BaseModule

init(autoreset=True)

class CredsExtractor(BaseModule):
    name = "CredsExtractor"

    def banner(self):
        print(f"{Fore.CYAN}CredsExtractor - Authorized Local Credential Search")

    def run(self):
        self.banner()
        print(f"{Fore.YELLOW}[!] Scanning authorized locations...")
        
        # Simple patterns for secrets
        patterns = [
            r'(?i)password\s*=\s*["\'](.*?)["\']',
            r'(?i)api_key\s*=\s*["\'](.*?)["\']',
            r'(?i)secret\s*=\s*["\'](.*?)["\']'
        ]
        
        # Files to scan
        files_to_scan = [".env", "secrets.json", ".bash_history"]
        
        for file in files_to_scan:
            if os.path.exists(file):
                print(f"{Fore.WHITE}[*] Checking {file}...")
                with open(file, "r") as f:
                    content = f.read()
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            print(f"{Fore.GREEN}[+] Found secret: {match}")
        
        print(f"{Fore.CYAN}[*] Done.")
        self.pause()
