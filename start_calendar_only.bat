@echo off
echo ======================================
echo   DENTAL KALENDER STARTEN
echo ======================================
echo.

cd dental-calendar

echo [1/2] Installiere Pakete...
call npm install

echo.
echo [2/2] Starte Kalender-Server...
echo.
echo Der Kalender laeuft auf: http://localhost:3005
echo.

npm start