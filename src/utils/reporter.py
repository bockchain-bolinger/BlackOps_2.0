import json
import glob
from colorama import Fore, init
from src.core.base_module import BaseModule

init(autoreset=True)

class Reporter(BaseModule):
    name = "Reporter"

    def banner(self):
        print(f"{Fore.CYAN}Reporter - Consolidating JSON Results")

    def run(self):
        self.banner()
        files = glob.glob("*.json")
        if not files:
            print(f"{Fore.RED}[!] No JSON files found.")
            self.pause()
            return
        
        print(f"{Fore.WHITE}[*] Found {len(files)} files. Generating summary...")
        summary = {}
        for file in files:
            if file == "secrets.json" or file == "sites.json": continue
            with open(file, "r") as f:
                try:
                    summary[file] = json.load(f)
                except json.JSONDecodeError:
                    print(f"{Fore.RED}[!] Error reading {file}")
        
        with open("summary_report.json", "w") as f:
            json.dump(summary, f, indent=4)
        
        print(f"{Fore.GREEN}[+] Summary saved to summary_report.json")
        self.pause()
