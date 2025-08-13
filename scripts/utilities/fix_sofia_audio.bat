@echo off
echo =====================================
echo Sofia Audio Fix
echo =====================================
echo.

echo Stopping all services...
taskkill /F /IM python.exe 2>nul
docker-compose -f docker-compose.simple.yml down

echo.
echo Waiting 5 seconds...
timeout /t 5 /nobreak > nul

echo.
echo [1/4] Starting LiveKit...
docker-compose -f docker-compose.simple.yml up -d livekit
timeout /t 5 /nobreak > nul

echo.
echo [2/4] Starting Calendar...
start cmd /k "cd dental-calendar && npm start"
timeout /t 3 /nobreak > nul

echo.
echo [3/4] Starting Sofia Web...
start cmd /k "python sofia_web.py"
timeout /t 3 /nobreak > nul

echo.
echo [4/4] Starting Sofia Agent with console output...
start cmd /k "python agent.py console"

echo.
echo =====================================
echo Services started!
echo =====================================
echo.
echo Test Sofia:
echo 1. Open http://localhost:3005
echo 2. Press F12 for browser console
echo 3. Click Sofia Agent button
echo 4. Look for audio debug info
echo.
echo If no audio:
echo - Check browser console for errors
echo - Try the debug buttons (bottom right)
echo - Make sure to allow microphone
echo.
pause