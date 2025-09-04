@echo off
echo 🚇 Sofia Voice Agent Tunneling Setup
echo =====================================
echo.

echo 📋 This will set up tunneling for your local Sofia agent
echo    so it can be accessed from the Railway web interface.
echo.

:: Check if ngrok is installed
echo 🔍 Checking for ngrok...
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ ngrok not found. Please install ngrok:
    echo.
    echo    Option 1: winget install ngrok
    echo    Option 2: Download from https://ngrok.com/download
    echo.
    echo Once installed, run this script again.
    pause
    exit /b 1
)

echo ✅ ngrok found!
echo.

echo 🤖 Starting Sofia Tunnel Bridge...
start "Sofia Bridge" cmd /c "python sofia-tunnel-bridge.py"

echo ⏳ Waiting for bridge to start...
timeout /t 3 /nobreak >nul

echo.
echo 🚇 Starting ngrok tunnel...
echo.
echo 📋 IMPORTANT: Copy the HTTPS URL that appears below
echo    This URL will connect your web interface to Sofia!
echo.

:: Start ngrok tunnel for the bridge
ngrok http 5000