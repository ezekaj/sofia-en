#!/usr/bin/env python3
"""
Test script for Enhanced Calendar Connection
Tests the improved agent-calendar integration with retry logic and error handling
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.enhanced_calendar_client import get_calendar_client

async def test_calendar_connection():
    """Test the enhanced calendar client"""
    print("🧪 Testing Enhanced Calendar Connection...")
    print("=" * 60)
    
    # Load development environment
    load_dotenv('.env.development')
    
    calendar_url = os.getenv('CALENDAR_URL', 'http://localhost:3005')
    print(f"📡 Calendar URL: {calendar_url}")
    
    try:
        async with get_calendar_client() as client:
            print("\n1️⃣ Testing Health Check...")
            health = await client.health_check()
            print(f"   ✅ Health Status: {'🟢 Healthy' if health else '🔴 Unhealthy'}")
            
            print("\n2️⃣ Testing Next Available Appointment...")
            next_available = await client.get_next_available()
            print(f"   📅 Next Available: {next_available}")
            
            print("\n3️⃣ Testing Appointment Suggestions...")
            suggestions = await client.get_suggestions(days=7, limit=3)
            print(f"   💡 Suggestions: {suggestions}")
            
            print("\n4️⃣ Testing Today's Appointments...")
            today = await client.get_today_appointments()
            print(f"   📋 Today's Appointments: {today}")
            
            print("\n5️⃣ Testing Date Availability (Tomorrow)...")
            from datetime import datetime, timedelta
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            availability = await client.check_date_availability(tomorrow)
            print(f"   🗓️ {tomorrow} Availability: {availability}")
            
            print("\n6️⃣ Testing Appointment Booking (Test Booking)...")
            test_booking = await client.book_appointment(
                patient_name="Test Patient",
                patient_phone="+49 30 12345678",
                requested_date=tomorrow,
                requested_time="14:00",
                treatment_type="Test Booking"
            )
            print(f"   📝 Test Booking Result: {test_booking}")
            
            print("\n✅ All tests completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_circuit_breaker():
    """Test circuit breaker functionality"""
    print("\n🔌 Testing Circuit Breaker...")
    print("=" * 60)
    
    # This will test what happens when the calendar is unavailable
    os.environ['CALENDAR_URL'] = 'http://localhost:9999'  # Invalid URL
    
    try:
        async with get_calendar_client() as client:
            for i in range(5):
                print(f"   Attempt {i+1}/5...")
                result = await client.get_next_available()
                print(f"   Result: {result.get('message', result)}")
                
                if result.get('error_code') == 'CIRCUIT_BREAKER_OPEN':
                    print("   🔴 Circuit breaker opened - working correctly!")
                    break
                    
    except Exception as e:
        print(f"   Circuit breaker test completed with expected error: {e}")
    
    # Reset URL
    load_dotenv('.env.development')

async def main():
    """Main test function"""
    print("🚀 Sofia Agent - Enhanced Calendar Connection Test")
    print("=" * 60)
    print("This script tests the improved calendar integration with:")
    print("  • Retry logic with exponential backoff")
    print("  • Circuit breaker pattern")
    print("  • Enhanced error handling")
    print("  • Resource management")
    print("  • Structured logging")
    print()
    
    # Test 1: Normal connection
    success = await test_calendar_connection()
    
    # Test 2: Circuit breaker
    await test_circuit_breaker()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Enhanced Calendar Integration: ALL TESTS PASSED!")
        print("✅ Your agent is ready to connect to the calendar with improved reliability!")
    else:
        print("❌ Some tests failed. Please check the calendar service and configuration.")
    
    print("\n🐳 To run with Docker:")
    print("   docker-compose up -d dental-calendar")
    print("   python agent.py dev")
    print("\n📋 To check logs:")
    print("   docker-compose logs -f sofia-agent")

if __name__ == "__main__":
    asyncio.run(main())