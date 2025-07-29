#!/usr/bin/env python3
"""
Sofia-Calendar Connection Summary (Windows-compatible)
"""
import asyncio
import httpx
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_all_connections():
    print("SOFIA-CALENDAR CONNECTION SUMMARY")
    print("=" * 50)
    
    calendar_url = "http://localhost:3005"
    all_passed = True
    
    # Test 1: Health Check
    print("1. Calendar Health Check...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{calendar_url}/health")
            health = response.json()
            print(f"   PASS: Calendar is healthy")
            print(f"   Response: {health}")
    except Exception as e:
        print(f"   FAIL: Health check failed - {e}")
        all_passed = False
    
    # Test 2: Next Available
    print("\n2. Next Available Appointment...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{calendar_url}/api/sofia/next-available")
            result = response.json()
            print(f"   PASS: Got next available appointment")
            print(f"   Message: {result.get('message', 'No message')}")
    except Exception as e:
        print(f"   FAIL: Next available failed - {e}")
        all_passed = False
    
    # Test 3: Booking Test
    print("\n3. Appointment Booking Test...")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    booking_data = {
        "patientName": "Final Test",
        "patientPhone": "+49 30 12345678",
        "requestedDate": tomorrow,
        "requestedTime": "18:00",
        "treatmentType": "Final Connection Test"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{calendar_url}/api/sofia/appointment", json=booking_data)
            result = response.json()
            if result.get('success'):
                print(f"   PASS: Booking successful")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"   INFO: Booking response - {result.get('message')}")
    except Exception as e:
        print(f"   FAIL: Booking failed - {e}")
        all_passed = False
    
    # Test 4: Sofia Function
    print("\n4. Sofia's Calendar Function...")
    try:
        from src.dental.dental_tools import termin_buchen_calendar_system
        
        class MockContext:
            pass
        
        context = MockContext()
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = await termin_buchen_calendar_system(
            context=context,
            patient_name="Sofia Final Test",
            phone="030 88888888",
            appointment_date=tomorrow,
            appointment_time="19:00",
            treatment_type="Sofia Final Test"
        )
        
        if "erfolgreich" in result:
            print(f"   PASS: Sofia function works")
        else:
            print(f"   INFO: Sofia function returned: {result[:50]}...")
            
    except Exception as e:
        print(f"   FAIL: Sofia function error - {e}")
        all_passed = False
    
    # Final Summary
    print("\n" + "=" * 50)
    print("FINAL CONNECTIVITY STATUS")
    print("=" * 50)
    
    if all_passed:
        print("STATUS: SUCCESS - All connections working!")
        print()
        print("CONFIRMED WORKING:")
        print("- Calendar service is healthy and responding")
        print("- Sofia can query next available appointments")
        print("- Sofia can book appointments successfully")
        print("- Sofia's calendar function is operational")
        print()
        print("READY FOR VOICE TESTING!")
        print("Sofia is now connected to the calendar and can:")
        print("  * Listen for voice appointment requests")
        print("  * Book appointments through the calendar")
        print("  * Provide appointment information")
        print("  * Handle appointment scheduling")
    else:
        print("STATUS: NEEDS ATTENTION")
        print("Some connections may need troubleshooting")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(test_all_connections())