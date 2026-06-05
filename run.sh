#!/usr/bin/env bash
# run.sh - BlackOps Framework Starter (Linux/macOS)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="${VENV_DIR}/bin/python"

echo ""
echo "  ██████╗ ██╗      █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ███████╗"
echo "  ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝"
echo "  ██████╔╝██║     ███████║██║     █████╔╝ ██║   ██║██████╔╝███████╗"
echo "  ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝ ╚════██║"
echo "  ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗╚██████╔╝██║     ███████║"
echo "  ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝"
echo ""

# Python pruefen
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 nicht gefunden. Bitte installieren."
    exit 1
fi

# Virtuelle Umgebung erstellen falls nicht vorhanden
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Erstelle virtuelle Umgebung..."
    python3 -m venv "$VENV_DIR"
fi

# Aktivieren
source "${VENV_DIR}/bin/activate"

# Dependencies installieren / aktualisieren
echo "[*] Pruefe Dependencies..."
pip install -q --upgrade pip
pip install -q -r "$SCRIPT_DIR/requirements.txt"

echo "[*] Starte BlackOps..."
echo ""
cd "$SCRIPT_DIR"
exec "$PYTHON" black_ops.py
