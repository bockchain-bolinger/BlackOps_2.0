"""
black_ops.py - Hauptmenü des BlackOps Frameworks
"""

import os
import subprocess
import sys
import time

from colorama import Fore, init

init(autoreset=True)

VERSION = "3.0"

TOOLS = {
    "1": {
        "name": "Social Hunter V7 (OSINT Framework)",
        "file": "src/modules/social_hunter_v7.py",
        "sudo": False,
    },
    "2": {"name": "GhostNet (Anonymity & MAC Changer)", "file": "src/modules/ghost_net.py", "sudo": True},
    "3": {"name": "TraceLess (Log Wiper & Cleaner)", "file": "src/modules/traceless.py", "sudo": True},
    "4": {"name": "NetScout Pro (Reconnaissance)", "file": "src/modules/netscout.py", "sudo": False},
    "5": {"name": "MetaSpy (Image Forensics)", "file": "src/modules/metaspy.py", "sudo": False},
    "6": {"name": "HashBreaker (Password Cracker)", "file": "src/modules/hashbreaker.py", "sudo": False},
    "7": {"name": "SilentPhish (Cloudflare Phishing)", "file": "src/modules/silent_phish.py", "sudo": False},
    "8": {"name": "VenomMaker (Payload Generator)", "file": "src/modules/venom_maker.py", "sudo": False},
    "9": {"name": "NeuroLink (AI Tactical Advisor)", "file": "src/modules/neurolink.py", "sudo": False},
    "10": {"name": "AirStrike (WiFi Jammer & Monitor)", "file": "src/modules/airstrike.py", "sudo": True},
    "11": {"name": "NetShark (ARP Spoofer / MITM)", "file": "src/modules/netshark.py", "sudo": True},
    "12": {"name": "CryptoVault (Decoder/Encoder)", "file": "src/modules/cryptovault.py", "sudo": False},
    "13": {"name": "DirFuzzer (Directory Discovery)", "file": "src/modules/dir_fuzzer.py", "sudo": False},
    "14": {"name": "CloudScanner (S3 Bucket Enumeration)", "file": "src/modules/cloud_scanner.py", "sudo": False},
    "15": {"name": "Reporter (Consolidate Results)", "file": "src/utils/reporter.py", "sudo": False},
    "16": {"name": "CredsExtractor (Local Secrets)", "file": "src/modules/creds_extractor.py", "sudo": False},
    "17": {"name": "HeartbeatGen (Traffic Simulation)", "file": "src/modules/heartbeat_gen.py", "sudo": False},
}


def is_admin() -> bool:
    if os.name == "nt":
        try:
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    return os.geteuid() == 0


def check_permissions():
    if not is_admin():
        print(f"{Fore.YELLOW}[WARNUNG] Kein Admin/Root - sudo-Tools werden nicht funktionieren.")
        time.sleep(2)


def launch_tool(tool_id: str):
    tool = TOOLS.get(tool_id)
    if not tool:
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, tool["file"])

    if not os.path.exists(filepath):
        print(f"\n{Fore.RED}[ERROR] Datei fehlt: {tool['file']}")
        input()
        return

    print(f"\n{Fore.GREEN}[*] Starte {tool['name']}...")
    time.sleep(0.5)

    exe = sys.executable
    try:
        if os.name == "nt":
            subprocess.run([exe, filepath])
        elif tool["sudo"] and not is_admin():
            subprocess.run(["sudo", exe, filepath])
        else:
            subprocess.run([exe, filepath])
    except Exception as e:
        # Globaler Handler: Tool-Fehler wirft den User nicht aus dem Framework
        print(f"\n{Fore.RED}[ERROR] Tool abgestuerzt: {e}")
        input(f"{Fore.WHITE}[ENTER] Zurueck zum Menue...")


def print_logo():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"""{Fore.RED}
    ____  __               __      ____            
   / __ )/ /____  _____   / /__   / __ \\____  _____
  / __  / / __  |/ ___/  / //_/  / / / / __ \\/ ___/
 / /_/ / / /_/ / /__    / ,<    / /_/ / /_/ (__  ) 
/_____/_/\\__,_/\\___/   /_/|_|   \\____/ .___/____/  
                                    /_/            
{Fore.WHITE}      >> ULTIMATE HACKING SUITE v{VERSION} <<
{Fore.YELLOW}      Operator (Instagram): artur_bo91
{Fore.GREEN}      Root: {"YES" if is_admin() else Fore.RED + "NO"}
""")


def main_menu():
    check_permissions()
    while True:
        print_logo()

        print(f"{Fore.CYAN}--- RECON & OSINT --------")
        print(f"{Fore.WHITE}  [1]  Social Hunter   [4]  NetScout Pro   [5]  MetaSpy")
        print(f"\n{Fore.CYAN}--- OFFENSIVE & NETWORK --")
        print(f"{Fore.WHITE}  [7]  SilentPhish     [8]  VenomMaker     [10] AirStrike")
        print(f"{Fore.WHITE}  [11] NetShark         [6]  HashBreaker")
        print(f"\n{Fore.CYAN}--- STEALTH & UTILS ------")
        print(f"{Fore.WHITE}  [2]  GhostNet         [3]  TraceLess      [12] CryptoVault")
        print(f"{Fore.WHITE}  [13] DirFuzzer        [14] CloudScanner   [15] Reporter")
        print(f"{Fore.WHITE}  [16] CredsExtractor   [17] HeartbeatGen")
        print(f"\n{Fore.CYAN}--- INTELLIGENCE ---------")
        print(f"{Fore.WHITE}  [9]  NeuroLink AI")
        print(f"\n{Fore.WHITE}  [99] Exit   [--version] Version")
        print(f"{Fore.RED}----------------------------------")

        c = input(f"{Fore.YELLOW}black@ops:~$ ").strip()

        if c == "99":
            print(f"\n{Fore.RED}System halt.")
            sys.exit(0)
        elif c == "--version":
            print(f"{Fore.CYAN}BlackOps Framework v{VERSION}")
            time.sleep(1)
        elif c in TOOLS:
            launch_tool(c)
        else:
            print(f"{Fore.RED}[!] Unbekannter Befehl: {c}")
            time.sleep(0.8)


if __name__ == "__main__":
    main_menu()
