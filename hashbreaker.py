"""
hashbreaker.py - Offline Dictionary Attack Tool
"""

import hashlib
import json

from colorama import Fore, init

from base_module import BaseModule
from config import DEFAULT_WORDLIST, HASHBREAKER_PROGRESS

init(autoreset=True)

ALGOS = {"1": "md5", "2": "sha1", "3": "sha256", "4": "sha512"}


class HashBreaker(BaseModule):
    name = "HashBreaker"

    def banner(self):
        self.clear()
        print(f"""{Fore.RED}
    __  __           __    ____                  __            
   / / / /___ ______/ /_  / __ )________  ____ _/ /_____  _____
  / /_/ / __ `/ ___/ __ \\/ __  / ___/ _ \\/ __ `/ //_/ _ \\/ ___/
 / __  / /_/ (__  ) / / / /_/ / /  /  __/ /_/ / ,< /  __/ /    
/_/ /_/\\__,_/____/_/ /_/_____/_/   \\___/\\__,_/_/|_|\\___/_/     
{Fore.WHITE}      >> OFFLINE DICTIONARY ATTACK TOOL <<
""")

    def crack(self, target_hash: str, wordlist_path: str, algo: str) -> dict:
        """
        Fuehrt den Angriff durch.
        Gibt ein dict zurueck: {"found": bool, "password": str|None, "attempts": int}
        """
        target_hash = target_hash.strip().lower()
        print(f"\n{Fore.WHITE}[*] Hash:     {Fore.YELLOW}{target_hash}")
        print(f"{Fore.WHITE}[*] Algo:     {Fore.CYAN}{algo.upper()}")
        print(f"{Fore.WHITE}[*] Wordlist: {wordlist_path}\n")

        result = {"found": False, "password": None, "attempts": 0}

        try:
            with open(wordlist_path, encoding="latin-1", errors="replace") as f:
                for i, line in enumerate(f):
                    password = line.rstrip("\n\r")
                    attempt = hashlib.new(
                        algo, password.encode("utf-8", errors="replace")
                    ).hexdigest()

                    if attempt == target_hash:
                        print(f"\n{Fore.GREEN}[SUCCESS] GEFUNDEN: >>> {password} <<<")
                        result.update({"found": True, "password": password, "attempts": i + 1})
                        return result

                    if i % HASHBREAKER_PROGRESS == 0 and i > 0:
                        print(f"\r{Fore.YELLOW}[*] {i:,} Versuche...", end="", flush=True)

            result["attempts"] = i + 1
            print(f"\n{Fore.RED}[-] Nicht gefunden. ({result['attempts']:,} Versuche)")

        except FileNotFoundError:
            print(f"{Fore.RED}[ERROR] Wordlist nicht gefunden: {wordlist_path}")
        except PermissionError:
            print(f"{Fore.RED}[ERROR] Keine Leseberechtigung: {wordlist_path}")

        return result

    def run(self):
        self.banner()
        print(f"{Fore.CYAN}Algorithmus:")
        for k, v in ALGOS.items():
            print(f"  [{k}] {v.upper()}")

        algo = ALGOS.get(input(f"\n{Fore.YELLOW}[?] Wahl: ").strip())
        if not algo:
            print(f"{Fore.RED}[!] Ungueltig.")
            return

        target = input(f"{Fore.GREEN}[?] Ziel-Hash: ").strip()
        if not target:
            print(f"{Fore.RED}[!] Kein Hash.")
            return

        wordlist = (
            input(f"{Fore.GREEN}[?] Wordlist [{DEFAULT_WORDLIST}]: ").strip() or DEFAULT_WORDLIST
        )

        result = self.crack(target, wordlist, algo)

        # JSON Export
        if result["found"] and self.confirm("Ergebnis als JSON speichern?"):
            filename = f"crack_result_{algo}_{result['attempts']}.json"
            try:
                with open(filename, "w") as f:
                    json.dump(result, f, indent=2)
                print(f"{Fore.GREEN}[OK] {filename}")
            except Exception as e:
                print(f"{Fore.RED}[ERROR] {e}")

        self.pause()


if __name__ == "__main__":
    HashBreaker().run()
