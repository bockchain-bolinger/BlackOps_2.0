"""
ghost_net.py - Privacy & Anonymity Toolkit
"""

import os
import random
import subprocess
import sys
import time

import requests
from colorama import Fore, init

from src.core.base_module import BaseModule
from src.core.config import IP_API_URL, REQUEST_TIMEOUT, TOR_PROXY

init(autoreset=True)


class GhostNet(BaseModule):
    name = "GhostNet"

    def __init__(self):
        self.interface = "eth0"
        self._session = requests.Session()

    def banner(self):
        self.clear()
        print(f"""{Fore.CYAN}
   ______  __  ______  __________  __   ________________
  / ____/ / / / / __ \\/ ___/_  __/ / | / / ____/_  __/
 / / __  / /_/ / / / /\\__ \\ / /   /  |/ / __/   / /   
/ /_/ / / __  / /_/ /___/ // /   / /|  / /___  / /    
\\____/ /_/ /_/\\____//____//_/   /_/ |_/_____/ /_/     
{Fore.YELLOW}   >> PRIVACY & ANONYMITY TOOLKIT <<
""")

    def check_identity(self, use_tor=False):
        mode = "TOR" if use_tor else "CLEARNET"
        print(f"\n{Fore.WHITE}[*] Identitaet pruefen ({mode})...")
        try:
            if use_tor:
                self._session.proxies = {"http": TOR_PROXY, "https": TOR_PROXY}
                res = self._session.get(IP_API_URL, timeout=REQUEST_TIMEOUT)
            else:
                res = requests.get(IP_API_URL, timeout=REQUEST_TIMEOUT)
            res.raise_for_status()
            d = res.json()
            c = Fore.GREEN if use_tor else Fore.RED
            print(f"   IP:       {c}{d.get('query')}")
            print(f"   Land:     {c}{d.get('country')} ({d.get('countryCode')})")
            print(f"   ISP:      {c}{d.get('isp')}")
            print(f"   Zeitzone: {c}{d.get('timezone')}")
            if use_tor:
                print(f"{Fore.GREEN}   [v] Tor aktiv.")
            else:
                print(f"{Fore.RED}   [!] Ungeschuetzt.")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {e}")
            if use_tor:
                print(f"{Fore.YELLOW}[TIPP] sudo service tor start")

    def _random_mac(self) -> str:
        """Vollstaendig zufaellige, lokal-administrierte Unicast-MAC."""
        first = (random.randint(0, 255) & 0xFC) | 0x02
        rest = [random.randint(0, 255) for _ in range(5)]
        return ":".join([f"{first:02x}"] + [f"{b:02x}" for b in rest])

    def get_current_mac(self) -> str:
        if os.name == "nt":
            try:
                out = subprocess.check_output("getmac /fo csv /nh", shell=True).decode()
                return out.split(",")[0].replace('"', "")
            except Exception:
                return "Unknown"
        path = f"/sys/class/net/{self.interface}/address"
        try:
            return open(path).read().strip() if os.path.exists(path) else "Interface nicht gefunden"
        except Exception:
            return "Unknown"

    def change_mac(self):
        print(f"\n{Fore.WHITE}[*] MAC Spoofing auf {self.interface}...")
        print(f"   Aktuell: {Fore.YELLOW}{self.get_current_mac()}")
        new_mac = self._random_mac()
        print(f"   Neu:     {Fore.CYAN}{new_mac}")
        if not self.confirm("MAC jetzt aendern?"):
            return
        try:
            for step, cmd in enumerate(
                [
                    ["sudo", "ip", "link", "set", self.interface, "down"],
                    ["sudo", "ip", "link", "set", self.interface, "address", new_mac],
                    ["sudo", "ip", "link", "set", self.interface, "up"],
                ],
                1,
            ):
                print(f"{Fore.WHITE}   [{step}/3] {' '.join(cmd[3:])}")
                subprocess.run(cmd, check=True)
            final = self.get_current_mac()
            if final.lower() == new_mac.lower():
                print(f"\n{Fore.GREEN}[OK] MAC geaendert: {final}")
            else:
                print(f"\n{Fore.RED}[FAIL] Aenderung fehlgeschlagen.")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[ERROR] {e}")

    def run(self):
        while True:
            self.banner()
            print(f"{Fore.WHITE}[1] Whoami (Clearnet)")
            print(f"{Fore.WHITE}[2] Tor Check")
            print(f"{Fore.WHITE}[3] MAC Changer")
            print(f"{Fore.WHITE}[4] Interface setzen (Aktuell: {self.interface})")
            print(f"{Fore.WHITE}[99] Exit")
            print(f"\n{Fore.CYAN}{'─' * 45}")

            choice = input(f"{Fore.YELLOW}[?] Auswahl: ").strip()
            if choice == "1":
                self.check_identity(False)
            elif choice == "2":
                self.check_identity(True)
            elif choice == "3":
                if os.name == "nt":
                    print(f"\n{Fore.RED}[!] Nur unter Linux verfuegbar.")
                else:
                    self.change_mac()
            elif choice == "4":
                self.interface = input("Interface (z.B. wlan0): ").strip()
            elif choice == "99":
                sys.exit(0)
            self.pause()


if __name__ == "__main__":
    if not GhostNet().is_admin():
        print(f"{Fore.YELLOW}[HINWEIS] Fuer MAC Changer als Root starten.")
        time.sleep(2)
    GhostNet().run()
