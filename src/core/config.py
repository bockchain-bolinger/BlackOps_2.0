"""
config.py - Zentrale Konfiguration fuer das BlackOps Framework
Alle hardcodierten Werte sind hier gebündelt.
"""

import os

from dotenv import load_dotenv

# --- .env laden ---
load_dotenv()

# --- Logging ---
LOG_FILE = "blackops.log"

# --- Netzwerk ---
REQUEST_TIMEOUT = 6  # Sekunden fuer HTTP-Requests
DNS_TIMEOUT = 4  # Sekunden fuer DNS-Abfragen
PORT_SCAN_TIMEOUT = 1  # Sekunden fuer Port-Scan
TOR_PROXY = "socks5://127.0.0.1:9050"
IP_API_URL = "https://ip-api.com/json/"

# --- Spider ---
SPIDER_MAX_PAGES = 30
SPIDER_MAX_DEPTH = 3

# --- HashBreaker ---
HASHBREAKER_PROGRESS = 100_000  # Fortschrittsanzeige alle N Versuche
DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"

# --- Social Hunter ---
USERNAME_SCAN_WORKERS = 15
SITES_JSON = "sites.json"

# --- Port Scanner ---
DEFAULT_PORTS = {
    21: "FTP",
    22: "SSH",
    25: "SMTP",
    80: "HTTP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
}

# --- NeuroLink ---
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0.7
NEUROLINK_MAX_HISTORY = 20  # Max. Nachrichten im Kontext (Token-Schutz)

# --- Secrets ---
SECRETS_FILE = "secrets.json"


# Umgebungsvariablen als Fallback fuer API-Keys
def get_secret(key: str, json_key: str) -> str | None:
    """
    Laedt einen API-Key: erst aus Umgebungsvariable, dann aus secrets.json.
    """
    # 1. Umgebungsvariable hat Vorrang (sicherer)
    env_val = os.environ.get(key)
    if env_val:
        return env_val

    # 2. Fallback: secrets.json
    if os.path.exists(SECRETS_FILE):
        import json

        try:
            with open(SECRETS_FILE) as f:
                data = json.load(f)
                return data.get(json_key)
        except (OSError, json.JSONDecodeError, KeyError):
            return None
    return None
