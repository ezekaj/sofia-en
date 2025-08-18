@echo off
echo ========================================
echo Starting Sofia Dental Practice System
echo For English Presentation
echo ========================================
echo.

echo Starting Dental Calendar Server...
start cmd /k "cd dental-calendar && npm start"

timeout /t 3

echo Starting Sofia Voice Agent...
start cmd /k "python agent.py dev"

timeout /t 2

echo ========================================
echo System Starting...
echo ========================================
echo.
echo Calendar UI: http://localhost:3005
echo.
echo Sofia is ready to receive calls!
echo.
echo Press any key to open the calendar in browser...
pause > nul
start http://localhost:3005

echo.
echo ========================================
echo PRESENTATION READY!
echo ========================================
echo.
echo To stop all services, close the command windows.
pause