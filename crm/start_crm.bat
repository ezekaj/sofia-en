@echo off
echo 🏥 Zahnarztpraxis Dr. Weber - CRM Dashboard
echo ==========================================
echo.
echo 📅 Starte CRM-Dashboard für Ihre Termine...
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert oder nicht im PATH
    echo Bitte installieren Sie Python von https://python.org
    pause
    exit /b 1
)

REM Installiere Flask falls nicht vorhanden
echo 📦 Installiere benötigte Pakete...
pip install -r requirements.txt

echo.
echo ✅ CRM-Dashboard wird gestartet...
echo 🌐 Öffnen Sie http://localhost:5000 in Ihrem Browser
echo 👤 Geben Sie Ihren Namen ein, um Ihre Termine zu sehen
echo.
echo ⚠️  Zum Beenden drücken Sie Ctrl+C
echo.

REM Starte Flask-App
python app.py

pause
