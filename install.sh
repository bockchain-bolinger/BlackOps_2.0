#!/bin/bash
# install.sh - Komplette Installation von BlackOps

set -e  # Bei Fehler abbrechen

echo -e "\n\033[1;36m[*] Installiere BlackOps Framework...\033[0m"

# Prüfe Python
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[ERROR] Python3 nicht gefunden!\033[0m"
    exit 1
fi

echo -e "\033[1;32m[✓] Python3 gefunden: $(python3 --version)\033[0m"

# Erstelle virtuelle Umgebung
echo -e "\n\033[1;36m[*] Erstelle virtuelle Umgebung...\033[0m"
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo -e "\033[1;32m[✓] Virtuelle Umgebung erstellt\033[0m"
else
    echo -e "\033[1;33m[!] Virtuelle Umgebung existiert bereits\033[0m"
fi

# Aktiviere virtuelle Umgebung
source venv/bin/activate

# Installiere Abhängigkeiten
echo -e "\n\033[1;36m[*] Installiere Python-Pakete...\033[0m"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "\033[1;32m[✓] Alle Python-Abhängigkeiten installiert\033[0m"

# System-Abhängigkeiten (nur Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "\n\033[1;36m[*] Installiere System-Pakete...\033[0m"
    
    # Prüfe ob apt verfügbar
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y aircrack-ng tor cloudflared
        echo -e "\033[1;32m[✓] System-Pakete installiert\033[0m"
    else
        echo -e "\033[1;33m[!] Nicht-apt System, bitte manuell installieren:\033[0m"
        echo "   - aircrack-ng"
        echo "   - tor"
        echo "   - cloudflared"
    fi
else
    echo -e "\033[1;33m[!] Nicht-Linux System. System-Pakete müssen manuell installiert werden.\033[0m"
fi

# Erstelle Beispiel-Konfiguration
echo -e "\n\033[1;36m[*] Prüfe Konfiguration...\033[0m"
if [[ ! -f "secrets.json" ]]; then
    echo -e "\033[1;33m[!] Erstelle secrets.json...\033[0m"
    cat > secrets.json << EOF
{
    "rapidapi_key": "DEIN_BREACHDIRECTORY_KEY_HIER",
    "openai_key": "DEIN_OPENAI_API_KEY_HIER"
}
EOF
    echo -e "\033[1;31m[!] WICHTIG: Bitte trage deine API-Keys in secrets.json ein!\033[0m"
else
    echo -e "\033[1;32m[✓] secrets.json existiert bereits\033[0m"
fi

# Mache run.sh ausführbar
chmod +x run.sh install.sh

echo -e "\n\033[1;32m═══════════════════════════════════════════════\033[0m"
echo -e "\033[1;32m[✓] Installation abgeschlossen!\033[0m"
echo -e "\n\033[1;36mStarte mit:\033[0m"
echo -e "  \033[1;33msudo ./run.sh\033[0m"
echo -e "\n\033[1;36mOder direkt:\033[0m"
echo -e "  \033[1;33msudo python3 black_ops.py\033[0m"
echo -e "\033[1;32m═══════════════════════════════════════════════\033[0m"