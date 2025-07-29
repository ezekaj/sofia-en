@echo off
echo ===================================
echo Starting Sofia Calendar Integration
echo ===================================

echo.
echo [1/4] Starting Dental Calendar...
start cmd /k "cd dental-calendar && npm start"
timeout /t 3 /nobreak > nul

echo.
echo [2/4] Starting Sofia Web Interface...
start cmd /k "python sofia_web.py"
timeout /t 3 /nobreak > nul

echo.
echo [3/4] Starting LiveKit Server...
start cmd /k "docker-compose up livekit"
timeout /t 5 /nobreak > nul

echo.
echo [4/4] Starting Sofia Agent...
start cmd /k "python agent.py dev"

echo.
echo ===================================
echo All services are starting...
echo ===================================
echo.
echo Calendar UI: http://localhost:3005
echo Sofia Web: http://localhost:5001
echo.
echo To test Sofia in calendar:
echo 1. Open http://localhost:3005
echo 2. Click the "Sofia Agent" button
echo 3. Allow microphone access
echo 4. Say: "Hallo Sofia, ich moechte einen Termin buchen"
echo.
pause