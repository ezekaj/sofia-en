@echo off
REM Sofia AI Demo - One-Click Startup for Investor Presentations
REM This script ensures flawless demo experience with zero technical complexity visible

title Sofia AI Demo System
color 0A

echo.
echo ==========================================
echo  🚀 Sofia AI Demo System v1.0
echo  Professional Investor Presentation Mode
echo ==========================================
echo.

REM Set environment variables for professional mode
set DEMO_MODE=investor
set LOG_LEVEL=ERROR
set PROFESSIONAL_UI=true
set AUTO_RECOVERY=true

REM Check Python availability
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check Node.js availability
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 16+ and try again.
    pause
    exit /b 1
)

REM Install Python dependencies if needed
if not exist "dental_env" (
    echo 🔧 Setting up Python environment...
    python -m venv dental_env
)

call dental_env\Scripts\activate.bat
pip install -q -r requirements.txt

REM Install Node.js dependencies if needed
if not exist "dental-calendar\node_modules" (
    echo 📦 Installing Node.js dependencies...
    cd dental-calendar
    npm install --silent
    cd ..
)

REM Clean up any previous processes
echo 🧹 Cleaning up previous sessions...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 >nul

REM Start the professional orchestrator
echo.
echo 🚀 Starting Sofia AI Demo System...
echo 📊 Monitor status at: http://localhost:9000
echo 🎯 Demo interface at: http://localhost:3005
echo.
echo ✅ System optimized for investor presentations
echo ⚡ All services will auto-start and self-heal
echo 🎪 Demo ready in less than 30 seconds
echo.

REM Launch orchestrator
python sofia-demo-orchestrator.py

REM If orchestrator exits, show professional message
echo.
echo ✅ Sofia AI Demo Session Complete
echo 📊 Thank you for using Sofia AI Professional Demo System
pause