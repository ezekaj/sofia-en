@echo off
echo 🚇 Setting up Sofia Voice Agent Tunneling...
echo.

:: Check if ngrok is installed
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ngrok not found. Installing...
    echo Please download ngrok from: https://ngrok.com/download
    echo Or use: winget install ngrok
    pause
    exit /b 1
)

echo ✅ ngrok found
echo.

:: Start Sofia agent in background
echo 🤖 Starting Sofia Agent...
start "Sofia Agent" cmd /k "cd /d %~dp0 && python agent.py dev"

:: Wait a moment for agent to start
timeout /t 5 /nobreak >nul

echo 🚇 Starting ngrok tunnel for Sofia...
echo This will create a public HTTPS URL for your local Sofia agent
echo.
echo 📋 Copy the HTTPS URL and update the web interface to connect to it
echo.

:: Start ngrok tunnel (assuming Sofia runs on port 8080 or similar)
ngrok http 8080

pause