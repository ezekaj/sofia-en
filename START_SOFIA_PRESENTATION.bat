@echo off
cls
echo ==========================================
echo     DR. SMITH'S DENTAL PRACTICE
echo     Sofia AI Assistant - English Version
echo     Presentation Setup
echo ==========================================
echo.

echo [1/4] Checking prerequisites...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    pause
    exit /b 1
)

echo [OK] Prerequisites checked
echo.

echo [2/4] Starting Dental Calendar System...
cd dental-calendar
start "Dental Calendar" cmd /k npm start
cd ..
timeout /t 5 >nul

echo [3/4] Opening Calendar in Browser...
start http://localhost:3005
timeout /t 2 >nul

echo [4/4] Ready for Voice Integration
echo.
echo ==========================================
echo     SYSTEM READY FOR PRESENTATION!
echo ==========================================
echo.
echo Calendar UI:  http://localhost:3005
echo.
echo FEATURES AVAILABLE:
echo - View calendar with appointments
echo - Create new appointments
echo - Real-time updates
echo - Sofia voice integration (requires LiveKit)
echo.
echo TO ADD VOICE SUPPORT:
echo 1. Install LiveKit server
echo 2. Run: livekit-server --dev
echo 3. Run: python agent.py dev
echo.
echo Press any key to open test page...
pause >nul
start test_calendar.html
echo.
echo ==========================================
echo To stop services, close the command windows
echo ==========================================
pause