"""
cryptovault.py - Encoding & Hashing Utility
"""

import base64
import codecs
import hashlib
import json
import sys

from colorama import Fore, init

from src.core.base_module import BaseModule

init(autoreset=True)


class CryptoVault(BaseModule):
    name = "CryptoVault"

    def banner(self):
        self.clear()
        print(f"""{Fore.MAGENTA}
   ______                 __        _    __            ____ 
  / ____/________  ____  / /_____  | |  / /___ ___  __/ / /_
 / /   / ___/ __ \\/ __ \\/ __/ __ \\ | | / / __ `/ / / / / __/
/ /___/ /  / /_/ / /_/ / /_/ /_/ / | |/ / /_/ / /_/ / / /_  
\\____/_/   \\__, / .___/\\__/\\____/  |___/\\__,_/\\__,_/_/\\__/  
          /____/_/                                          
{Fore.WHITE}   >> ENCODING & HASHING UTILITY <<
""")

    def run(self):
        operations = {
            "1": ("Base64 Encode", self._b64_encode),
            "2": ("Base64 Decode", self._b64_decode),
            "3": ("Hash generieren", self._hash_text),
            "4": ("ROT13 Cipher", self._rot13),
            "5": ("Hex Encode", self._hex_encode),
            "6": ("Hex Decode", self._hex_decode),
            "7": ("Hash-Datei pruefen", self._hash_file),
        }

        while True:
            self.banner()
            for k, (label, _) in operations.items():
                print(f"{Fore.WHITE}[{k}] {label}")
            print(f"{Fore.WHITE}[99] Exit")
            print(f"\n{Fore.CYAN}{'─' * 40}")

            choice = input(f"{Fore.YELLOW}[?] Wahl: ").strip()
            if choice == "99":
                sys.exit(0)
            if choice in operations:
                operations[choice][1]()
            else:
                print(f"{Fore.RED}[!] Ungueltig.")
            self.pause()

    # ─── Operationen ──────────────────────────────────────────────────────────

    def _b64_encode(self):
        txt = input("Text: ")
        result = base64.b64encode(txt.encode()).decode()
        print(f"{Fore.GREEN}Result: {result}")
        self._offer_export(result)

    def _b64_decode(self):
        txt = input("Base64 String: ")
        try:
            result = base64.b64decode(txt).decode()
            print(f"{Fore.GREEN}Result: {result}")
            self._offer_export(result)
        except Exception:
            print(f"{Fore.RED}[ERROR] Kein gueltiges Base64.")

    def _hash_text(self):
        txt = input("Text: ")
        enc = txt.encode()
        results = {
            "MD5": hashlib.md5(enc).hexdigest(),
            "SHA1": hashlib.sha1(enc).hexdigest(),
            "SHA256": hashlib.sha256(enc).hexdigest(),
            "SHA512": hashlib.sha512(enc).hexdigest(),
        }
        for algo, h in results.items():
            print(f"{Fore.GREEN}{algo:8s}: {h}")
        if self.confirm("Als JSON exportieren?"):
            fname = f"hashes_{hashlib.md5(enc).hexdigest()[:8]}.json"
            with open(fname, "w") as f:
                json.dump({"input": txt, "hashes": results}, f, indent=2)
            print(f"{Fore.GREEN}[OK] {fname}")

    def _rot13(self):
        txt = input("Text: ")
        print(f"{Fore.GREEN}Result: {codecs.encode(txt, 'rot_13')}")

    def _hex_encode(self):
        txt = input("Text: ")
        result = txt.encode().hex()
        print(f"{Fore.GREEN}Result: {result}")
        self._offer_export(result)

    def _hex_decode(self):
        txt = input("Hex String: ").replace(" ", "")
        try:
            result = bytes.fromhex(txt).decode()
            print(f"{Fore.GREEN}Result: {result}")
            self._offer_export(result)
        except ValueError:
            print(f"{Fore.RED}[ERROR] Kein gueltiges Hex.")

    def _hash_file(self):
        path = input("Dateipfad: ").strip()
        import os

        if not os.path.exists(path):
            print(f"{Fore.RED}[ERROR] Datei nicht gefunden.")
            return
        try:
            data = open(path, "rb").read()
            print(f"{Fore.GREEN}MD5:    {hashlib.md5(data).hexdigest()}")
            print(f"{Fore.GREEN}SHA256: {hashlib.sha256(data).hexdigest()}")
            print(f"{Fore.GREEN}SHA512: {hashlib.sha512(data).hexdigest()}")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {e}")

    def _offer_export(self, result: str):
        if self.confirm("In Datei speichern?"):
            fname = input("Dateiname: ").strip() or "output.txt"
            try:
                with open(fname, "w") as f:
                    f.write(result)
                print(f"{Fore.GREEN}[OK] {fname}")
            except Exception as e:
                print(f"{Fore.RED}[ERROR] {e}")


if __name__ == "__main__":
    CryptoVault().run()
