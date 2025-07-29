#!/usr/bin/env python3
"""
Direct test of Sofia-Calendar booking functionality
This bypasses the web UI and tests the core connection
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_direct_booking():
    print("DIRECT SOFIA-CALENDAR CONNECTION TEST")
    print("=" * 50)
    print("Testing the core booking functionality without web UI")
    print()
    
    # Import Sofia's booking function
    from src.dental.dental_tools import termin_buchen_calendar_system
    
    # Mock the context that Sofia provides
    class MockContext:
        pass
    
    context = MockContext()
    
    # Test booking for tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("TEST 1: Booking appointment for tomorrow")
    print(f"Date: {tomorrow}")
    print("Time: 10:00")
    print("Patient: Direct Test Patient")
    print()
    
    try:
        result = await termin_buchen_calendar_system(
            context=context,
            patient_name="Direct Test Patient",
            phone="030 12345678",
            appointment_date=tomorrow,
            appointment_time="10:00",
            treatment_type="Kontrolluntersuchung"
        )
        
        print("RESULT:")
        print("-" * 30)
        # Extract the message without emojis for Windows compatibility
        clean_result = result.replace('✅', '[SUCCESS]').replace('❌', '[FAIL]').replace('🏥', '[CLINIC]')
        print(clean_result)
        print("-" * 30)
        
        if "erfolgreich gebucht" in result:
            print("\nSTATUS: SUCCESS - Appointment booked!")
            print("Sofia successfully connected to calendar and booked the appointment.")
            return True
        else:
            print("\nSTATUS: BOOKING ISSUE")
            print("Sofia connected but booking may have failed.")
            return False
            
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Sofia could not connect to calendar.")
        return False

async def test_availability_check():
    print("\nTEST 2: Checking next available appointment")
    print("-" * 30)
    
    from src.utils.enhanced_calendar_client import get_calendar_client
    
    try:
        async with get_calendar_client() as client:
            result = await client.get_next_available()
            
            if result.get('available'):
                print(f"Next available: {result.get('message', 'Unknown')}")
                print("STATUS: SUCCESS - Calendar responding to queries")
                return True
            else:
                print("No availability information")
                return False
                
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def main():
    print("This test verifies Sofia can book appointments")
    print("without requiring the web interface.\n")
    
    # Test 1: Direct booking
    booking_ok = await test_direct_booking()
    
    # Test 2: Availability check
    availability_ok = await test_availability_check()
    
    # Summary
    print("\n" + "=" * 50)
    print("CONNECTION SUMMARY")
    print("=" * 50)
    
    if booking_ok and availability_ok:
        print("RESULT: SOFIA-CALENDAR CONNECTION IS WORKING!")
        print()
        print("The core connection between Sofia and the calendar")
        print("is functional. The web UI error is a separate issue")
        print("related to LiveKit WebSocket connectivity.")
        print()
        print("Sofia CAN:")
        print("- Book appointments in the calendar")
        print("- Query available appointment times")
        print("- Process patient booking requests")
        print()
        print("The 'Failed to fetch' error in the browser is")
        print("a frontend connectivity issue, not a Sofia issue.")
    else:
        print("RESULT: Connection needs attention")
        print(f"Booking: {'OK' if booking_ok else 'FAILED'}")
        print(f"Availability: {'OK' if availability_ok else 'FAILED'}")

if __name__ == "__main__":
    # Ensure we're using the right environment
    os.environ['CALENDAR_URL'] = 'http://localhost:3005'
    asyncio.run(main())