"""
black_ops.py - Hauptmenü des BlackOps Frameworks
"""

from __future__ import annotations

import os
import sys
import time

from colorama import Fore, init

from src.core.runtime_helpers import clear_screen, patched_input, safe_input
from src.core.tool_registry import TOOL_REGISTRY

init(autoreset=True)
VERSION = "3.1"


def is_admin() -> bool:
    if os.name == "nt":
        try:
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    return os.geteuid() == 0


def check_permissions() -> None:
    if not is_admin():
        print(f"{Fore.YELLOW}[WARNUNG] Kein Admin/Root - sudo-Tools werden nicht funktionieren.")
        time.sleep(1.5)


def _render_banner() -> None:
    clear_screen()
    root_state = "YES" if is_admin() else "NO"
    tool_count = len(TOOL_REGISTRY)
    logo_lines = [
        r" ____  _        _    ____ _  _____  ____  ____  ",
        r"| __ )| |      / \  / ___| |/ / _ \|  _ \/ ___| ",
        "|  _ \\| |     / _ \\| |   | ' / | | | |_) \\___ " + "\\",
        r"| |_) | |___ / ___ \ |___| . \ |_| |  __/ ___) |",
        r"|____/|_____/_/   \_\____|_|\_\___/|_|   |____/  ",
        "",
    ]
    print(f"{Fore.RED}╔════════════════════════════════════════════════════════════╗")
    for idx, line in enumerate(logo_lines):
        color = Fore.RED if idx % 2 == 0 else Fore.LIGHTRED_EX
        print(f"║{color}{line:^60}{Fore.RED}║")
    print(f"║{Fore.WHITE}{f'BLACKOPS v{VERSION}  •  Root: {root_state}  •  Tools: {tool_count}':^60}{Fore.RED}║")
    print(f"║{Fore.LIGHTWHITE_EX}{'registry-driven launcher • premium menu • direct dispatch':^60}{Fore.RED}║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║{Fore.LIGHTWHITE_EX}{'99=Exit  •  --help  •  --version  •  13+ integrated':^60}{Fore.RED}║")
    print("╚════════════════════════════════════════════════════════════╝")


def _format_tool_row(entries) -> str:
    parts = []
    for entry in entries:
        label = f"[{entry.tool_id}] {entry.name}"
        parts.append(f"{Fore.WHITE}{label}")
    return "   ".join(parts)


def _render_menu() -> None:
    grouped = TOOL_REGISTRY.grouped()
    sections = [
        ("RECON & OSINT", "Recon & OSINT"),
        ("NETWORK", "Network"),
        ("STEALTH & UTILS", "Stealth & Utils"),
        ("INTELLIGENCE", "Intelligence"),
        ("ANALYSIS / BINARY", "Analysis / Binary"),
    ]
    accent_palette = [
        Fore.RED,
        Fore.LIGHTRED_EX,
        Fore.RED,
        Fore.LIGHTRED_EX,
        Fore.RED,
    ]
    for index, (title, key) in enumerate(sections, start=1):
        accent = accent_palette[(index - 1) % len(accent_palette)]
        entries = grouped.get(key, [])
        print(f"{accent}{'▣ ' + title + ' ▣':^60}")
        if not entries:
            print(f"{Fore.LIGHTWHITE_EX}{'  (keine Tools)':^60}")
        else:
            for entry in entries:
                print(
                    f"{Fore.LIGHTRED_EX}  [{Fore.WHITE}{entry.tool_id:>2}{Fore.LIGHTRED_EX}] "
                    f"{Fore.WHITE}{entry.name}"
                )
        if index != len(sections):
            print(f"{accent}{'─' * 60}")
    print(f"\n{Fore.LIGHTWHITE_EX}  [99] Exit   [--version] Version   [--help] Hilfe")
    print(f"{Fore.RED}{'─' * 60}")
    print(f"{Fore.LIGHTRED_EX}Hint: Tools 13+ are now registry-backed and launch directly.")


def launch_tool(tool_id: str) -> None:
    entry = TOOL_REGISTRY.get(tool_id)
    if not entry:
        return

    try:
        tool_cls = entry.load_class()
    except Exception as exc:
        print(f"\n{Fore.RED}[ERROR] Tool konnte nicht geladen werden: {exc}")
        return

    print(f"\n{Fore.GREEN}[*] Starte {entry.name}...")
    time.sleep(0.35)

    if entry.sudo and not is_admin():
        print(f"{Fore.YELLOW}[!] Hinweis: {entry.name} kann Root/Admin erwarten.")

    try:
        with patched_input(default=""):
            tool = tool_cls()
            run = getattr(tool, "run", None)
            if callable(run):
                run()
            elif callable(tool):
                tool()
            else:
                raise AttributeError(f"{entry.class_name} hat keinen run()-Entrypoint")
    except SystemExit:
        return
    except KeyboardInterrupt:
        return
    except EOFError:
        return
    except Exception as exc:
        print(f"\n{Fore.RED}[ERROR] Tool abgestuerzt: {exc}")
        if sys.stdin.isatty():
            try:
                input(f"{Fore.WHITE}[ENTER] Zurueck zum Menue...")
            except (EOFError, OSError):
                pass


def main_menu() -> None:
    check_permissions()
    while True:
        _render_banner()
        _render_menu()

        choice = safe_input(f"{Fore.YELLOW}black@ops:~$ ", strip=True)
        if not choice:
            print(f"{Fore.RED}[!] Keine interaktive Eingabe verfuegbar. Beende.")
            sys.exit(0)

        if choice == "99":
            print(f"\n{Fore.RED}System halt.")
            sys.exit(0)
        if choice == "--version":
            print(f"{Fore.CYAN}BlackOps Framework v{VERSION}")
            time.sleep(1)
            continue
        if choice == "--help":
            print(
                """BlackOps v3.1

Start:
  ./run.sh
  python black_ops.py

Navigation:
  99        Exit
  --help    Show this help
  --version Show version

Status:
  Registry-driven launcher with grouped categories and safe non-TTY handling.
"""
            )
            time.sleep(1)
            continue
        if choice in TOOL_REGISTRY:
            launch_tool(choice)
        else:
            print(f"{Fore.RED}[!] Unbekannter Befehl: {choice}")
            time.sleep(0.8)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        print(f"BlackOps Framework v{VERSION}")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(
            """BlackOps v3.1

Usage:
  python black_ops.py            Start interactive menu
  python black_ops.py --version  Show version
  python black_ops.py --help     Show this help
"""
        )
        sys.exit(0)
    main_menu()
