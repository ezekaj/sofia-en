@echo off
echo =====================================
echo Starting Sofia with Correct Settings
echo =====================================
echo.

echo [1] Stopping old services...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak > nul

echo.
echo [2] Starting Sofia Agent in CONNECT mode...
echo This will make Sofia join rooms automatically
echo.

cd /d C:\Users\User\OneDrive\Desktop\eloelo\elo-deu
python agent.py connect --room sofia-room

pause