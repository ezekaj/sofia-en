#!/usr/bin/env python3
"""
Development Startup Script for Sofia Agent
Starts the agent with enhanced calendar integration in development mode
"""
import os
import sys
import subprocess
import time
import asyncio
from dotenv import load_dotenv

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    try:
        import httpx
        import tenacity
        print("   ✅ httpx - OK")
        print("   ✅ tenacity - OK")
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        print("   Installing missing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return False
    
    return True

def check_docker_services():
    """Check if required Docker services are running"""
    print("🐳 Checking Docker services...")
    
    try:
        # Check if docker-compose is available
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("   ❌ docker-compose not found")
            return False
        
        # Check if services are running
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True)
        
        if 'dental-calendar' in result.stdout and 'Up' in result.stdout:
            print("   ✅ dental-calendar service - Running")
        else:
            print("   ⚠️ dental-calendar service - Not running")
            print("   Starting calendar service...")
            subprocess.run(['docker-compose', 'up', '-d', 'dental-calendar'])
            time.sleep(5)
        
        if 'livekit' in result.stdout and 'Up' in result.stdout:
            print("   ✅ livekit service - Running")
        else:
            print("   ⚠️ livekit service - Not running")
            print("   Starting livekit service...")
            subprocess.run(['docker-compose', 'up', '-d', 'livekit'])
            time.sleep(5)
            
    except Exception as e:
        print(f"   ❌ Docker check failed: {e}")
        return False
    
    return True

async def test_calendar_connection():
    """Test if calendar connection works"""
    print("🔗 Testing calendar connection...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from src.utils.enhanced_calendar_client import get_calendar_client
        
        async with get_calendar_client() as client:
            health = await client.health_check()
            if health:
                print("   ✅ Calendar connection - OK")
                return True
            else:
                print("   ❌ Calendar connection - Failed")
                return False
                
    except Exception as e:
        print(f"   ❌ Calendar connection test failed: {e}")
        return False

def setup_environment():
    """Setup development environment"""
    print("⚙️ Setting up development environment...")
    
    # Copy .env.development to .env if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.development'):
            import shutil
            shutil.copy('.env.development', '.env')
            print("   ✅ Environment file created from .env.development")
        else:
            print("   ⚠️ No environment file found")
    
    # Load environment
    load_dotenv('.env.development')
    
    print(f"   📡 Calendar URL: {os.getenv('CALENDAR_URL', 'http://localhost:3005')}")
    print(f"   🎤 LiveKit URL: {os.getenv('LIVEKIT_URL', 'ws://localhost:7880')}")
    print(f"   📊 Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")

def start_agent():
    """Start the Sofia agent in development mode"""
    print("🚀 Starting Sofia Agent in development mode...")
    print("=" * 60)
    print("🎯 Agent will start with:")
    print("   • Enhanced calendar integration")
    print("   • Retry logic and circuit breaker")
    print("   • Detailed debug logging")
    print("   • Resource management")
    print("   • Health monitoring")
    print()
    print("📋 To stop the agent: Ctrl+C")
    print("🐳 To view all logs: docker-compose logs -f")
    print("=" * 60)
    
    try:
        # Start the agent with development mode
        subprocess.run([sys.executable, 'agent.py', 'dev'])
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting agent: {e}")

async def main():
    """Main function"""
    print("🏥 Sofia Dental Assistant - Development Startup")
    print("=" * 60)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Please install dependencies and try again")
        return
    
    # Step 2: Setup environment
    setup_environment()
    
    # Step 3: Check Docker services
    if not check_docker_services():
        print("❌ Please ensure Docker is running and try again")
        return
    
    # Step 4: Test calendar connection
    connection_ok = await test_calendar_connection()
    if not connection_ok:
        print("⚠️ Calendar connection failed, but agent will still start")
        print("   Make sure the calendar service is running: docker-compose up -d dental-calendar")
    
    # Step 5: Start the agent
    start_agent()

if __name__ == "__main__":
    asyncio.run(main())