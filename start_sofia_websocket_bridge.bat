@echo off
REM Sofia WebSocket Bridge Startup Script
REM This script starts the WebSocket bridge for Sofia voice agent integration

echo ================================================
echo      Sofia WebSocket Bridge Startup
echo ================================================
echo.

echo Checking requirements...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python: OK

REM Check if required packages are installed
echo Checking Python packages...
python -c "import websockets, speech_recognition" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Some required packages may be missing
    echo Installing required packages...
    pip install websockets speechrecognition pyaudio
)

echo Packages: OK

REM Check if calendar server port is available
echo Checking calendar server...
netstat -an | find "3005" >nul
if %errorlevel% equ 0 (
    echo Calendar Server: Running on port 3005
) else (
    echo WARNING: Calendar server not running on port 3005
    echo Please start the calendar server first: cd dental-calendar && npm start
)

REM Check if WebSocket port is available
echo Checking WebSocket port...
netstat -an | find "8081" >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 8081 is already in use
    echo Another instance might be running
) else (
    echo WebSocket Port 8081: Available
)

echo.
echo ================================================
echo      Starting Sofia WebSocket Bridge
echo ================================================
echo.
echo Bridge will start on: ws://localhost:8081
echo Test interface: http://localhost:3005/sofia-websocket-test.html
echo Calendar interface: http://localhost:3005
echo.
echo Press Ctrl+C to stop the bridge
echo.

REM Start the WebSocket bridge
python sofia_websocket_bridge.py --dev --host localhost --port 8081

echo.
echo Bridge stopped.
pause