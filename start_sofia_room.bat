@echo off
echo =====================================
echo Sofia Room Connection Fix
echo =====================================
echo.

REM Stop existing Python processes
echo Stopping existing services...
taskkill /F /IM python.exe 2>nul

echo.
echo Starting Sofia Agent for room "sofia-room"...
echo.

REM Set environment variables
set LIVEKIT_URL=ws://localhost:7880
set LIVEKIT_API_KEY=devkey
set LIVEKIT_API_SECRET=secret
set PYTHONIOENCODING=utf-8

REM Start agent with specific room configuration
echo Starting agent with room configuration...
python -c "import os; os.environ['LIVEKIT_DEFAULT_ROOM'] = 'sofia-room'; import agent; agent.main()"

pause