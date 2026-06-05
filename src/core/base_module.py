"""
base_module.py - Gemeinsame Basisklasse fuer alle BlackOps Module
"""

import logging
import os
import sys

from colorama import Fore, init

from src.core.config import LOG_FILE

init(autoreset=True)

# --- Zentrales Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout) if os.environ.get("DEBUG_LOG") else logging.NullHandler(),
    ],
)


class BaseModule:
    """Basisklasse mit gemeinsamen Funktionen fuer alle Module."""

    name = "BaseModule"

    def __init__(self):
        self.logger = logging.getLogger(self.name)
        self._check_admin()

    def _check_admin(self):
        """Optionaler Admin-Check - wird von Subklassen ueberschrieben wenn noetig."""
        pass

    def is_admin(self) -> bool:
        if os.name == "nt":
            try:
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                return False
        else:
            return os.geteuid() == 0

    def require_admin(self):
        """Beendet das Programm wenn kein Admin/Root."""
        if not self.is_admin():
            msg = f"'{self.name}' benoetigt Root/Admin-Rechte!"
            print(f"{Fore.RED}[CRITICAL] {msg}")
            self.logger.critical(msg)
            sys.exit(1)

    def banner(self):
        """Wird von Subklassen implementiert."""
        raise NotImplementedError

    def run(self):
        """Wird von Subklassen implementiert."""
        raise NotImplementedError

    @staticmethod
    def clear():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def pause(msg="[ENTER] Zurueck..."):
        input(f"\n{Fore.WHITE}{msg}")

    @staticmethod
    def confirm(question: str) -> bool:
        return input(f"{Fore.YELLOW}[?] {question} (y/n): ").strip().lower() == "y"
