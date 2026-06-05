"""
neurolink.py - AI Tactical Advisor (GPT-4o)
"""

import sys

from colorama import Fore, init

try:
    from openai import OpenAI
except ImportError:
    print("Bitte installiere: pip install openai")
    sys.exit(1)

from src.core.base_module import BaseModule
from src.core.config import NEUROLINK_MAX_HISTORY, OPENAI_MODEL, OPENAI_TEMPERATURE, get_secret

init(autoreset=True)

SYSTEM_PROMPT = (
    "You are 'NeuroLink', an advanced cybersecurity AI integrated into the Black Ops Framework. "
    "You provide precise, technical advice on ethical hacking, penetration testing, and security research. "
    "You help with tools like Nmap, Metasploit, Burp Suite, and Python scripting. "
    "Always remind users to only test systems they own or have explicit permission to test. "
    "Keep answers concise and technical."
)


class NeuroLink(BaseModule):
    name = "NeuroLink"

    def __init__(self, initial_context=None):
        self.api_key = get_secret("OPENAI_API_KEY", "openai_key")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        if initial_context:
            self.history.append({"role": "user", "content": f"Context: {initial_context}"})

    def banner(self):
        self.clear()
        print(f"""{Fore.GREEN}
   _   __                     __    _       __  
  / | / /__  __  ___________ / /   (_)___  / /__
 /  |/ / _ \\/ / / / ___/ __ \\/ /   / / __ \\/ //_/
/ /|  /  __/ /_/ / /  / /_/ / /___/ / / / / ,<   
/_/ |_/\\___/\\__,_/_/   \\____/_____/_/_/ /_/_/|_|  
{Fore.WHITE}   >> AI TACTICAL ADVISOR ({OPENAI_MODEL}) <<
""")

    def _trim_history(self):
        """Begrenzt History auf MAX_HISTORY Nachrichten (verhindert Token-Overflow)."""
        if len(self.history) > NEUROLINK_MAX_HISTORY + 1:
            self.history = [self.history[0]] + self.history[-NEUROLINK_MAX_HISTORY:]

    def _key_valid(self) -> bool:
        return bool(self.client and self.api_key and "DEIN-" not in self.api_key)

    def run(self):
        self.banner()

        if not self._key_valid():
            print(f"{Fore.RED}[ERROR] Kein gueltiger OpenAI Key.")
            print(f"{Fore.WHITE}Setze OPENAI_API_KEY als Umgebungsvariable oder in secrets.json.")
            self.pause()
            return

        print(f"{Fore.CYAN}[OK] NeuroLink online. 'exit' / '99' zum Beenden.")
        print(f"{Fore.WHITE}     'clear' setzt den Konversationsverlauf zurueck.\n")

        while True:
            try:
                user_input = input(f"{Fore.GREEN}Operator > {Fore.WHITE}").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "99"]:
                    break
                if user_input.lower() == "clear":
                    self.history = [self.history[0]]
                    print(f"{Fore.YELLOW}[*] Verlauf zurueckgesetzt.")
                    continue

                self.history.append({"role": "user", "content": user_input})
                self._trim_history()

                print(f"{Fore.YELLOW}[...] ", end="", flush=True)
                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL, messages=self.history, temperature=OPENAI_TEMPERATURE
                )
                answer = response.choices[0].message.content
                usage = response.usage

                print(f"\r{Fore.CYAN}NeuroLink > {Fore.WHITE}{answer}")
                print(
                    f"{Fore.WHITE}            {Fore.WHITE}[Tokens: {usage.prompt_tokens} in / {usage.completion_tokens} out]\n"
                )

                self.history.append({"role": "assistant", "content": answer})

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n{Fore.RED}[ERROR] {e}")
                break


if __name__ == "__main__":
    NeuroLink().run()
