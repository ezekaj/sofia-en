@echo off
echo Starting Sofia Agent with Enhanced Calendar Integration in Docker...
echo.

echo Step 1: Starting Calendar Service...
docker-compose up -d dental-calendar
timeout /t 5 /nobreak > nul

echo Step 2: Checking Calendar Health...
curl -s http://localhost:3005/health
echo.

echo Step 3: Starting Sofia Agent...
docker-compose up -d sofia-agent
timeout /t 5 /nobreak > nul

echo Step 4: Checking Agent Health...
curl -s http://localhost:8080/health
echo.

echo.
echo ===== SERVICES RUNNING =====
docker-compose ps
echo.

echo ===== VIEW LOGS =====
echo To view Sofia Agent logs: docker-compose logs -f sofia-agent
echo To view Calendar logs: docker-compose logs -f dental-calendar
echo To stop all services: docker-compose down
echo.

echo Sofia Agent is now running with enhanced features:
echo - Retry logic with exponential backoff
echo - Circuit breaker for calendar failures  
echo - Resource management and connection pooling
echo - Structured logging with privacy protection
echo.
echo Access the web interface at: http://localhost:5001
echo Monitor health at: http://localhost:8080/health