"""
social_hunter_v7.py - OSINT Framework
"""

import argparse
import asyncio
import concurrent.futures
import json
import os
import random
import re
import sys
import time
from collections import deque
from datetime import datetime
from urllib.parse import urljoin, urlparse

import aiohttp
import phonenumbers
import requests
from bs4 import BeautifulSoup
from colorama import Fore, init
from fpdf import FPDF
from phonenumbers import carrier, geocoder

from src.core.base_module import BaseModule
from src.core.config import (
    REQUEST_TIMEOUT,
    SITES_JSON,
    SPIDER_MAX_DEPTH,
    SPIDER_MAX_PAGES,
    USERNAME_SCAN_WORKERS,
    get_secret,
)

init(autoreset=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]


class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "Social Hunter - Security Audit Report", 0, 1, "C")
        self.line(10, 20, 200, 20)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, "L", 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font("Courier", "", 10)
        body = body.encode("latin-1", "replace").decode("latin-1")
        self.multi_cell(0, 10, body)
        self.ln()


class SocialHunterV7(BaseModule):
    name = "Social Hunter V7"

    def __init__(self):
        self.results = []
        self.target_display = ""
        self.scan_type = ""
        self.pdf_mode = False
        self.verbose = False
        self.api_key = get_secret("RAPIDAPI_KEY", "rapidapi_key")

    def banner(self):
        self.clear()
        print(f"""{Fore.CYAN}
   _____            _       __  __            __           
  / ___/____  _____(_)___ _/ / / /_  ______  / /____  _____
  \\__ \\/ __ \\/ ___/ / __ `/ / / / / / / __ \\/ __/ _ \\/ ___/
 ___/ / /_/ / /__/ / /_/ / / / / /_/ / / / / /_/  __/ /    
/____/\\____/\\___/_/\\__,_/_/_/_/\\__,_/_/ /_/\\__/\\___/_/     
{Fore.YELLOW}      >> THE ULTIMATE OSINT FRAMEWORK V7 <<
""")

    def _headers(self):
        return {"User-Agent": random.choice(USER_AGENTS)}

    def run(self):
        dispatch = {
            "1": (self.scan_username, "Username: "),
            "2": (self.scan_ip, "IP Adresse: "),
            "3": (self.scan_phone, "Telefonnummer (+49...): "),
            "4": (self.scan_dorks, "Domain (z.B. firma.com): "),
            "5": (self.scan_spider, "URL (z.B. firma.com): "),
            "6": (self.scan_leaks, "Email/User: "),
            "7": (self.scan_metadata, "Bild-URL: "),
        }
        while True:
            self.banner()
            print(f"{Fore.WHITE}[1] Username Search   [2] IP Intelligence")
            print(f"{Fore.WHITE}[3] Phone Analysis    [4] Google Dorking")
            print(f"{Fore.WHITE}[5] Email Spider      [6] Breach Check")
            print(f"{Fore.WHITE}[7] MetaData Scan     [99] Exit")
            print(f"\n{Fore.CYAN}{'─' * 45}")

            choice = input(f"{Fore.YELLOW}[?] Modul: ").strip()
            if choice == "99":
                sys.exit(0)
            if choice not in dispatch:
                print(f"{Fore.RED}[!] Ungueltig.")
                time.sleep(1)
                continue

            self.results = []
            self.pdf_mode = self.confirm("PDF-Bericht erstellen?")
            func, prompt = dispatch[choice]
            func(input(f"{Fore.GREEN}[+] {prompt}").strip())

            if self.pdf_mode:
                self.generate_pdf()
            self.pause()

    def generate_pdf(self):
        if not self.results:
            return
        filename = f"Report_{self.scan_type}_{datetime.now().strftime('%H%M%S')}.pdf"
        print(f"\n{Fore.YELLOW}[PDF] Erstelle {filename}...")
        try:
            pdf = PDFReport()
            pdf.add_page()
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Target: {self.target_display}", 0, 1)
            pdf.cell(0, 10, f"Module: {self.scan_type}", 0, 1)
            pdf.ln(10)
            for item in self.results:
                pdf.chapter_title(item["title"])
                pdf.chapter_body(item["content"])
            pdf.output(filename)
            print(f"{Fore.GREEN}[OK] {filename} gespeichert.")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] PDF: {e}")

    def _export_json(self, filename: str):
        """Optionaler JSON-Export der Scan-Ergebnisse."""
        try:
            with open(filename, "w") as f:
                json.dump(
                    {
                        "target": self.target_display,
                        "module": self.scan_type,
                        "results": self.results,
                    },
                    f,
                    indent=2,
                )
            print(f"{Fore.GREEN}[OK] JSON: {filename}")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] JSON Export: {e}")

    # ─── MODULE ───────────────────────────────────────────────────────────────

    def scan_metadata(self, url):
        self.target_display = url
        self.scan_type = "Metadata"
        print(f"\n{Fore.WHITE}[*] Analysiere Metadaten von: {url}")
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            img = ExifImage(BytesIO(r.content))
            if not img.has_exif:
                print(f"{Fore.YELLOW}[!] Keine EXIF-Daten gefunden.")
                return

            info = "\n".join([f"{attr}: {getattr(img, attr)}" for attr in img.list_all()])
            print(f"{Fore.GREEN}{info}")
            self.results.append({"title": "Metadata", "content": info})
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Metadaten: {e}")

    def scan_leaks(self, query):
        self.target_display = query
        self.scan_type = "Breach"
        if not self.api_key or "DEIN_KEY" in self.api_key:
            print(f"{Fore.RED}[ERROR] API Key fehlt (RAPIDAPI_KEY env oder secrets.json).")
            return
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "breachdirectory.p.rapidapi.com",
        }
        try:
            r = requests.get(
                "https://breachdirectory.p.rapidapi.com/",
                headers=headers,
                params={"func": "auto", "term": query},
                timeout=REQUEST_TIMEOUT,
            )
            r.raise_for_status()
            data = r.json()
            leaks = data.get("result", []) if data.get("success") else []
            if not leaks:
                print(f"{Fore.GREEN}[+] Keine Leaks gefunden.")
                return
            print(f"{Fore.RED}[!] {len(leaks)} Leak(s)!")
            report = ""
            for leak in leaks:
                line = f"Quelle: {leak.get('sources')}\nHash: {leak.get('hash')}\n---"
                print(f"{Fore.RED}{line}")
                report += line + "\n"
            self.results.append({"title": "Leaks", "content": report})
        except requests.RequestException as e:
            print(f"{Fore.RED}[ERROR] {e}")

    async def _fetch_url(self, session, url):
        try:
            async with session.get(url, headers=self._headers(), timeout=4) as response:
                return await response.text()
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}    [SKIP] {url}: {e}")
            return None

    async def _run_spider_async(self, start_url):
        found = set()
        visited = set()
        queue = deque([start_url])
        base = urlparse(start_url).netloc
        depth_map = {start_url: 0}
        count = 0

        async with aiohttp.ClientSession() as session:
            while queue and count < SPIDER_MAX_PAGES:
                curr = queue.popleft()
                if curr in visited or depth_map.get(curr, 0) > SPIDER_MAX_DEPTH:
                    continue

                visited.add(curr)
                count += 1
                print(f"{Fore.WHITE}  [{count}/{SPIDER_MAX_PAGES}] {curr[:70]}")

                html = await self._fetch_url(session, curr)
                if not html:
                    continue

                for m in re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", html):
                    if m not in found:
                        print(f"{Fore.GREEN}    [EMAIL] {m}")
                        found.add(m)

                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all("a", href=True):
                    full = urljoin(curr, a["href"])
                    if urlparse(full).netloc == base and full not in visited:
                        queue.append(full)
                        depth_map[full] = depth_map.get(curr, 0) + 1

        print(f"\n{Fore.CYAN}[+] {len(found)} Email(s) gefunden.")
        return list(found)

    def scan_spider(self, url):
        self.target_display = url
        self.scan_type = "Spider"
        if not url.startswith("http"):
            url = "https://" + url
        print(f"\n{Fore.WHITE}[*] Spider: {url}")

        try:
            emails = asyncio.run(self._run_spider_async(url))
            self.results.append({"title": "Emails", "content": "\n".join(emails) or "Keine"})
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Spider gestoppt.")

    def scan_username(self, username):
        self.target_display = username
        self.scan_type = "UserEnum"
        if not os.path.exists(SITES_JSON):
            print(f"{Fore.RED}[ERROR] {SITES_JSON} fehlt!")
            return
        with open(SITES_JSON) as f:
            sites = json.load(f)
        found = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=USERNAME_SCAN_WORKERS) as ex:
            futures = {ex.submit(self._check_site, username, n, d): n for n, d in sites.items()}
            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result(timeout=10)
                    if res:
                        print(f"{Fore.GREEN}[+] {res[0]} -> {res[1]}")
                        self.results.append({"title": res[0], "content": res[1]})
                        found += 1
                except Exception as e:
                    if self.verbose:
                        print(f"{Fore.RED}[DEBUG] {futures[future]}: {e}")
        print(f"\n{Fore.CYAN}[+] {found} Profil(e) gefunden.")

    def _check_site(self, user, name, data):
        url = data["url"].format(user)
        try:
            r = requests.get(url, headers=self._headers(), timeout=5)
            if data["error_type"] == "status" and r.status_code == 200:
                return (name, url)
            if (
                data["error_type"] == "message"
                and r.status_code == 200
                and data["error_msg"] not in r.text
            ):
                return (name, url)
        except requests.RequestException:
            pass
        return None

    def scan_ip(self, ip):
        self.target_display = ip
        self.scan_type = "IPIntel"
        # Einfache IP-Validierung
        import ipaddress

        try:
            ipaddress.ip_address(ip)
        except ValueError:
            print(f"{Fore.RED}[ERROR] Ungueltige IP-Adresse: {ip}")
            return
        try:
            r = requests.get(f"https://ip-api.com/json/{ip}", timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            d = r.json()
            if d.get("status") == "fail":
                print(f"{Fore.RED}[-] IP Lookup fehlgeschlagen.")
                return
            info = (
                f"IP:       {d.get('query')}\nISP:      {d.get('isp')}\n"
                f"Org:      {d.get('org')}\nLand:     {d.get('country')} ({d.get('countryCode')})\n"
                f"Stadt:    {d.get('city')}\nZeitzone: {d.get('timezone')}"
            )
            print(f"{Fore.GREEN}{info}")
            self.results.append({"title": "IP Data", "content": info})
        except requests.RequestException as e:
            print(f"{Fore.RED}[ERROR] {e}")

    def scan_phone(self, num):
        self.target_display = num
        self.scan_type = "PhoneIntel"
        try:
            pn = phonenumbers.parse(num, None)
            if not phonenumbers.is_valid_number(pn):
                print(f"{Fore.RED}[-] Ungueltige Nummer.")
                return
            info = (
                f"Nummer:   {phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}\n"
                f"Region:   {geocoder.description_for_number(pn, 'de')}\n"
                f"Anbieter: {carrier.name_for_number(pn, 'de')}"
            )
            print(f"{Fore.GREEN}{info}")
            self.results.append({"title": "Phone Data", "content": info})
        except phonenumbers.phonenumberutil.NumberParseException as e:
            print(f"{Fore.RED}[ERROR] {e}")

    def scan_dorks(self, domain):
        self.target_display = domain
        self.scan_type = "Dorks"
        # Domain-Validierung
        if not re.match(r"^(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}$", domain):
            print(f"{Fore.RED}[ERROR] Ungueltige Domain: {domain}")
            return
        dorks = [
            ("Config Files", f"site:{domain} ext:conf OR ext:env OR ext:xml"),
            ("Login Pages", f"site:{domain} inurl:login OR inurl:admin"),
            ("Open Dirs", f'site:{domain} intitle:"index of"'),
            ("SQL Errors", f'site:{domain} "sql syntax" OR "mysql_fetch"'),
            ("Subdomains", f"site:*.{domain}"),
        ]
        print(f"\n{Fore.CYAN}Google Dorks fuer {domain}:\n")
        for name, query in dorks:
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            print(f"{Fore.GREEN}[+] {name}:\n    {Fore.WHITE}{url}\n")
            self.results.append({"title": name, "content": url})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Social Hunter V7")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--username")
    group.add_argument("-i", "--ip")
    group.add_argument("-p", "--phone")
    group.add_argument("-d", "--dork")
    group.add_argument("-s", "--spider")
    group.add_argument("-l", "--leak")
    parser.add_argument("--pdf", action="store_true")
    parser.add_argument("--json", action="store_true", help="JSON Export")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--version", action="version", version="Social Hunter V7 v3.0")

    tool = SocialHunterV7()

    if len(sys.argv) == 1:
        tool.run()
    else:
        args = parser.parse_args()
        tool.pdf_mode = args.pdf
        tool.verbose = args.verbose
        if args.username:
            tool.scan_username(args.username)
        elif args.ip:
            tool.scan_ip(args.ip)
        elif args.phone:
            tool.scan_phone(args.phone)
        elif args.dork:
            tool.scan_dorks(args.dork)
        elif args.spider:
            tool.scan_spider(args.spider)
        elif args.leak:
            tool.scan_leaks(args.leak)
        if tool.pdf_mode:
            tool.generate_pdf()
        if args.json:
            tool._export_json(f"export_{tool.scan_type}.json")
