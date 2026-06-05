"""
traceless.py - System Cleaner & Log Wiper (Root erforderlich)
"""

import os
import subprocess
import sys

from colorama import Fore, init

from src.core.base_module import BaseModule

init(autoreset=True)

LINUX_LOGS = [
    "/var/log/auth.log",
    "/var/log/syslog",
    "/var/log/messages",
    "/var/log/wtmp",
    "/var/log/btmp",
    "/var/log/lastlog",
]


class TraceLess(BaseModule):
    name = "TraceLess"

    def __init__(self):
        self.is_win = os.name == "nt"

    def _check_admin(self):
        self.require_admin()

    def banner(self):
        self.clear()
        print(f"""{Fore.RED}
  ______                      __                
 /_  __/________ _________   / /   ___  _____ _____
  / / / ___/ __ `/ ___/ _ \\ / /   / _ \\/ ___// ___/
 / / / /  / /_/ / /__/  __// /___/  __(__  )(__  ) 
/_/ /_/   \\__,_/\\___/\\___//_____/\\___/____//____/  
{Fore.WHITE}   >> SYSTEM CLEANER & LOG WIPER <<
""")

    def _secure_delete(self, path: str) -> bool:
        if not os.path.exists(path):
            return False
        if not self.is_win:
            try:
                subprocess.run(
                    ["shred", "-u", "-z", "-n", "3", path], stderr=subprocess.DEVNULL, check=True
                )
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        # Python-Fallback: 3-Pass Overwrite
        try:
            size = os.path.getsize(path)
            with open(path, "wb") as f:
                for _ in range(3):
                    f.write(os.urandom(size))
                    f.seek(0)
                f.write(b"\x00" * size)
            os.remove(path)
            return True
        except Exception:
            return False

    def wipe_logs(self):
        print(f"\n{Fore.WHITE}[*] Bereinige Logs...")
        if self.is_win:
            try:
                logs = (
                    subprocess.check_output(["wevtutil", "el"], stderr=subprocess.DEVNULL)
                    .decode()
                    .splitlines()
                )
                count = sum(
                    1
                    for log in logs
                    if log.strip()
                    and subprocess.run(
                        ["wevtutil", "cl", log.strip()], stderr=subprocess.DEVNULL
                    ).returncode
                    == 0
                )
                print(f"{Fore.GREEN}[OK] {count} Event Logs bereinigt.")
            except Exception as e:
                print(f"{Fore.RED}[ERROR] {e}")
        else:
            count = 0
            for log in LINUX_LOGS:
                if not os.path.exists(log):
                    continue
                try:
                    subprocess.run(["shred", "-n", "1", log], stderr=subprocess.DEVNULL)
                    open(log, "w").close()
                    print(f"{Fore.GREEN}  [+] {log}")
                    count += 1
                except PermissionError:
                    print(f"{Fore.RED}  [-] Keine Rechte: {log}")
            print(f"{Fore.GREEN}[OK] {count} Logs bereinigt.")

    def wipe_history(self):
        print(f"\n{Fore.WHITE}[*] Bereinige Command-History...")
        if self.is_win:
            ps_hist = os.path.expandvars(
                r"%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
            )
            if self._secure_delete(ps_hist):
                print(f"{Fore.GREEN}  [+] PowerShell History geloescht.")
            subprocess.run(["powershell", "-Command", "Clear-History"], stderr=subprocess.DEVNULL)
        else:
            targets = [os.path.expanduser("~/.bash_history")]
            if os.geteuid() == 0:
                targets.append("/root/.bash_history")
            for hist in targets:
                if self._secure_delete(hist):
                    print(f"{Fore.GREEN}  [+] Geschreddert: {hist}")
                else:
                    print(f"{Fore.WHITE}  [.] Nicht gefunden: {hist}")
            os.system("history -c && history -w")

    def run(self):
        while True:
            self.banner()
            log_label = "Event Logs" if self.is_win else "syslog / auth.log"
            hist_label = "PowerShell" if self.is_win else "Bash History"
            print(f"{Fore.WHITE}[1] Wipe Logs ({log_label})")
            print(f"{Fore.WHITE}[2] Wipe History ({hist_label})")
            print(f"{Fore.WHITE}[3] NUCLEAR (Alles bereinigen)")
            print(f"{Fore.WHITE}[99] Exit")
            print(f"\n{Fore.CYAN}{'─' * 45}")

            choice = input(f"{Fore.YELLOW}[?] Auswahl: ").strip()
            if choice == "1":
                self.wipe_logs()
            elif choice == "2":
                self.wipe_history()
            elif choice == "3":
                if self.confirm("NUCLEAR: Alles loeschen?"):
                    self.wipe_logs()
                    self.wipe_history()
                    print(f"\n{Fore.GREEN}[*] Abgeschlossen.")
                    sys.exit(0)
            elif choice == "99":
                sys.exit(0)
            self.pause()


if __name__ == "__main__":
    TraceLess().run()
