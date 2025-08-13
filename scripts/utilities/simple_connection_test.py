#!/usr/bin/env python3
"""
Simple Sofia-Calendar connection test without emojis
"""
import asyncio
import httpx
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_connection():
    print("SOFIA-CALENDAR CONNECTION TEST")
    print("=" * 50)
    
    calendar_url = "http://localhost:3005"
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{calendar_url}/health")
            print(f"   Health check: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
    
    # Test 2: Sofia's main endpoint
    print("2. Testing Sofia's main endpoint...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{calendar_url}/api/sofia/next-available")
            result = response.json()
            print(f"   Next available: {result.get('message', 'No message')}")
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
    
    # Test 3: Booking functionality
    print("3. Testing booking functionality...")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    booking_data = {
        "patientName": "Connection Test",
        "patientPhone": "+49 30 12345678",
        "requestedDate": tomorrow,
        "requestedTime": "14:30",
        "treatmentType": "Connection Test"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(f"{calendar_url}/api/sofia/appointment", json=booking_data)
            result = response.json()
            success = result.get('success', False)
            print(f"   Booking result: {'SUCCESS' if success else 'FAILED'}")
            print(f"   Message: {result.get('message', 'No message')}")
            return success
        except Exception as e:
            print(f"   ERROR: {e}")
            return False

async def test_sofia_function():
    print("4. Testing Sofia's function directly...")
    try:
        from src.dental.dental_tools import termin_buchen_calendar_system
        
        # Mock context
        class MockContext:
            pass
        
        context = MockContext()
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = await termin_buchen_calendar_system(
            context=context,
            patient_name="Sofia Test",
            phone="030 99999999",
            appointment_date=tomorrow,
            appointment_time="15:30",
            treatment_type="Sofia Test"
        )
        
        # Check if booking was successful (contains success message)
        if "erfolgreich gebucht" in result or "gebucht" in result:
            print("   Sofia function: SUCCESS")
            return True
        else:
            print("   Sofia function: FAILED or needs attention")
            print(f"   Result: {result[:100]}...")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

async def main():
    connection_ok = await test_connection()
    sofia_ok = await test_sofia_function()
    
    print("\n" + "=" * 50)
    print("FINAL RESULTS:")
    print(f"Calendar Connection: {'OK' if connection_ok else 'FAILED'}")
    print(f"Sofia Integration: {'OK' if sofia_ok else 'FAILED'}")
    
    if connection_ok and sofia_ok:
        print("\nSUCCESS: Sofia-Calendar connection is working!")
        print("Sofia can now book appointments through the calendar.")
    else:
        print("\nISSUE: Some connections need attention.")
        
    return connection_ok and sofia_ok

if __name__ == "__main__":
    asyncio.run(main())