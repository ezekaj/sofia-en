@echo off
echo =====================================
echo Sofia Calendar Hybrid Setup
echo =====================================
echo.
echo This will start:
echo - LiveKit Server (Docker)
echo - Dental Calendar (Local)
echo - Sofia Agent (Local)
echo.

echo [1/3] Starting LiveKit Server in Docker...
docker-compose -f docker-compose.simple.yml up -d livekit
timeout /t 5 /nobreak > nul

echo.
echo [2/3] Starting Dental Calendar locally...
start cmd /k "cd dental-calendar && npm start"
timeout /t 3 /nobreak > nul

echo.
echo [3/3] Starting Sofia Agent locally...
start cmd /k "python agent.py dev"

echo.
echo =====================================
echo All services starting...
echo =====================================
echo.
echo LiveKit Server: ws://localhost:7880
echo Calendar UI: http://localhost:3005
echo.
echo To test Sofia:
echo 1. Open http://localhost:3005
echo 2. Click "Sofia Agent" button
echo 3. Allow microphone access
echo 4. Say: "Hallo Sofia"
echo.
pause