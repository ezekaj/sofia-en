#!/usr/bin/env python3
"""
Simple test for enhanced calendar connection without emojis
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_calendar():
    print("Testing Enhanced Calendar Connection...")
    print("=" * 50)
    
    # Load development environment
    load_dotenv('.env.development')
    
    calendar_url = os.getenv('CALENDAR_URL', 'http://localhost:3005')
    print(f"Calendar URL: {calendar_url}")
    
    try:
        from src.utils.enhanced_calendar_client import get_calendar_client
        
        async with get_calendar_client() as client:
            print("1. Testing Health Check...")
            health = await client.health_check()
            print(f"   Health Status: {'HEALTHY' if health else 'UNHEALTHY'}")
            
            print("2. Testing Next Available...")
            next_available = await client.get_next_available()
            print(f"   Result: {next_available}")
            
            if health:
                print("SUCCESS: Calendar connection is working!")
                return True
            else:
                print("WARNING: Calendar service is not responding")
                return False
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("Sofia Agent - Enhanced Calendar Test")
    print("=" * 50)
    
    success = await test_calendar()
    
    if success:
        print("\nNEXT STEPS:")
        print("1. Start calendar service: docker-compose up -d dental-calendar")
        print("2. Run agent: python agent.py dev")
    else:
        print("\nTROUBLESHOOT:")
        print("1. Make sure calendar service is running")
        print("2. Check docker-compose logs dental-calendar")

if __name__ == "__main__":
    asyncio.run(main())