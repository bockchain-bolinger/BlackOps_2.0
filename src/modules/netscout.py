"""
netscout.py - Reconnaissance Tool (interaktiv + CLI)
"""

import argparse
import asyncio
import json
import re
import socket
import sys
from datetime import datetime

import dns.resolver
import requests
from colorama import Fore, init

from src.core.base_module import BaseModule
from src.core.config import DEFAULT_PORTS, DNS_TIMEOUT, PORT_SCAN_TIMEOUT, REQUEST_TIMEOUT

init(autoreset=True)

DOMAIN_RE = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")


class NetScout(BaseModule):
    name = "NetScout Pro"

    def banner(self):
        self.clear()
        print(f"""{Fore.CYAN}
╔════════════════════════════════════════╗
║      NETSCOUT - RECONNAISSANCE TOOL   ║
╚════════════════════════════════════════╝
""")

    def _validate_domain(self, domain: str) -> str:
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        if not DOMAIN_RE.match(domain):
            print(f"{Fore.RED}[ERROR] Ungueltige Domain: '{domain}'")
            sys.exit(1)
        return domain

    def run(self):
        """Interaktiver Modus."""
        self.banner()
        domain = self._validate_domain(input(f"{Fore.GREEN}[?] Ziel-Domain: ").strip())
        verbose = self.confirm("Detaillierte Ausgabe?")

        scout = NetScoutRunner(domain, verbose)
        scout.print_header()
        scout.check_http_headers()
        scout.get_dns_records()

        if self.confirm("Port-Scan durchfuehren?"):
            asyncio.run(scout.scan_ports())

        if self.confirm("Ergebnisse als JSON exportieren?"):
            scout.export_json()

        self.pause()


class NetScoutRunner:
    """Kapselt einen einzelnen Scan-Lauf."""

    def __init__(self, domain: str, verbose: bool = False):
        self.domain = domain
        self.verbose = verbose
        self.results = {}

    def print_header(self):
        print(f"{Fore.WHITE}[*] Ziel:      {Fore.YELLOW}{self.domain}")
        print(f"{Fore.WHITE}[*] Start:     {datetime.now().strftime('%H:%M:%S')}\n")

    def check_http_headers(self):
        print(f"{Fore.BLUE}[INFO] HTTP-Header...")
        try:
            r = requests.get(f"https://{self.domain}", timeout=REQUEST_TIMEOUT)
            server = r.headers.get("Server", "Unknown")
            x_powered = r.headers.get("X-Powered-By")
            print(f"{Fore.GREEN}  [+] Status: {r.status_code}")
            print(f"{Fore.GREEN}  [+] Server: {server}")
            if x_powered:
                print(f"{Fore.YELLOW}  [!] X-Powered-By: {x_powered}")

            missing = []
            for h in [
                "X-Frame-Options",
                "Content-Security-Policy",
                "Strict-Transport-Security",
                "X-Content-Type-Options",
                "Referrer-Policy",
            ]:
                if h not in r.headers:
                    print(f"{Fore.RED}  [-] Fehlt: {h}")
                    missing.append(h)
                elif self.verbose:
                    print(f"{Fore.GREEN}  [+] {h}: {r.headers[h][:60]}")

            self.results["http"] = {
                "status": r.status_code,
                "server": server,
                "missing_headers": missing,
            }
        except requests.RequestException as e:
            print(f"{Fore.RED}  [ERROR] {e}")

    def get_dns_records(self):
        print(f"\n{Fore.BLUE}[INFO] DNS-Records...")
        dns_data = {}
        for rtype in ["A", "AAAA", "MX", "NS", "TXT"]:
            try:
                answers = dns.resolver.resolve(self.domain, rtype, lifetime=DNS_TIMEOUT)
                records = [r.to_text() for r in answers]
                dns_data[rtype] = records
                for r in records:
                    print(f"{Fore.GREEN}  [+] {rtype:5s}: {r}")
            except dns.resolver.NoAnswer:
                if self.verbose:
                    print(f"{Fore.WHITE}  [.] {rtype:5s}: kein Eintrag")
            except dns.resolver.NXDOMAIN:
                print(f"{Fore.RED}  [-] NXDOMAIN")
                break
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}  [ERR] {rtype}: {e}")
        self.results["dns"] = dns_data

    async def _scan_port(self, ip, port, service):
        try:
            conn = asyncio.open_connection(ip, port)
            _, writer = await asyncio.wait_for(conn, timeout=PORT_SCAN_TIMEOUT)
            writer.close()
            await writer.wait_closed()
            print(f"{Fore.GREEN}  [+] {port:5d} ({service}) OFFEN")
            return port
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            if self.verbose:
                print(f"{Fore.WHITE}  [.] {port:5d} ({service}) geschlossen")
            return None

    async def scan_ports(self):
        print(f"\n{Fore.BLUE}[INFO] Port-Scan (Async)...")
        try:
            ip = socket.gethostbyname(self.domain)
            print(f"{Fore.WHITE}  [*] {self.domain} -> {ip}")
        except socket.gaierror as e:
            print(f"{Fore.RED}  [ERROR] DNS: {e}")
            return

        tasks = [self._scan_port(ip, p, s) for p, s in DEFAULT_PORTS.items()]
        results = await asyncio.gather(*tasks)
        open_ports = [r for r in results if r is not None]
        self.results["ports"] = open_ports

    def export_json(self):
        filename = f"netscout_{self.domain}_{datetime.now().strftime('%H%M%S')}.json"
        try:
            with open(filename, "w") as f:
                json.dump({"domain": self.domain, "results": self.results}, f, indent=2)
            print(f"{Fore.GREEN}[OK] Exportiert: {filename}")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] JSON: {e}")


def main():
    parser = argparse.ArgumentParser(description="NetScout - Recon Tool")
    parser.add_argument("target", help="Ziel-Domain")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--scan-ports", action="store_true")
    parser.add_argument("--json", action="store_true", help="JSON Export")
    parser.add_argument("--version", action="version", version="NetScout v3.0")
    args = parser.parse_args()

    domain = args.target.replace("https://", "").replace("http://", "").split("/")[0]
    if not DOMAIN_RE.match(domain):
        print(f"{Fore.RED}[ERROR] Ungueltige Domain.")
        sys.exit(1)

    runner = NetScoutRunner(domain, args.verbose)
    runner.print_header()
    runner.check_http_headers()
    runner.get_dns_records()
    if args.scan_ports:
        asyncio.run(runner.scan_ports())
    if args.json:
        runner.export_json()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        try:
            NetScout().run()
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Abbruch.")
    else:
        try:
            main()
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Abbruch.")
