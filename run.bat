@echo off
:: run.bat - BlackOps Framework Starter (Windows)
setlocal

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%.venv
set PYTHON=%VENV_DIR%\Scripts\python.exe

echo.
echo   ██████╗ ██╗      █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ███████╗
echo   ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝
echo   ██████╔╝██║     ███████║██║     █████╔╝ ██║   ██║██████╔╝███████╗
echo   ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝ ╚════██║
echo   ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗╚██████╔╝██║     ███████║
echo   ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝
echo.

:: Python pruefen
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nicht gefunden. Bitte installieren und PATH setzen.
    pause
    exit /b 1
)

:: Virtuelle Umgebung erstellen falls nicht vorhanden
if not exist "%VENV_DIR%" (
    echo [*] Erstelle virtuelle Umgebung...
    python -m venv "%VENV_DIR%"
)

:: Aktivieren
call "%VENV_DIR%\Scripts\activate.bat"

:: Dependencies installieren
echo [*] Pruefe Dependencies...
pip install -q --upgrade pip
pip install -q -r "%SCRIPT_DIR%requirements.txt"

echo [*] Starte BlackOps...
echo.
cd /d "%SCRIPT_DIR%"
python black_ops.py

pause