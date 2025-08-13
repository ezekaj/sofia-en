#!/usr/bin/env python3
"""
Test ONLY the connection between Sofia and Calendar - no changes to Sofia
"""
import asyncio
import os
import sys
import httpx
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_direct_calendar_endpoints():
    """Test all calendar endpoints that Sofia uses"""
    print("Testing Direct Calendar Endpoints from Sofia's Perspective...")
    print("=" * 60)
    
    calendar_url = "http://localhost:3005"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Health Check
        print("1. Testing /health endpoint...")
        try:
            response = await client.get(f"{calendar_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 2: Next Available (Sofia uses this)
        print("\n2. Testing /api/sofia/next-available...")
        try:
            response = await client.get(f"{calendar_url}/api/sofia/next-available")
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Available: {result.get('available')}")
            print(f"   Message: {result.get('message')}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 3: Appointment Booking (Main Sofia function)
        print("\n3. Testing /api/sofia/appointment (POST)...")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        booking_data = {
            "patientName": "Sofia Connection Test",
            "patientPhone": "+49 30 99999999",
            "requestedDate": tomorrow,
            "requestedTime": "15:00",
            "treatmentType": "Connection Test"
        }
        try:
            response = await client.post(f"{calendar_url}/api/sofia/appointment", json=booking_data)
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            if result.get('appointment'):
                print(f"   Appointment ID: {result['appointment'].get('id')}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 4: Date Availability Check
        print("\n4. Testing /api/sofia/check-date/{date}...")
        try:
            response = await client.get(f"{calendar_url}/api/sofia/check-date/{tomorrow}")
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Available: {result.get('available')}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 5: Today's Appointments
        print("\n5. Testing /api/sofia/today...")
        try:
            response = await client.get(f"{calendar_url}/api/sofia/today")
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Appointments: {len(result.get('appointments', []))}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 6: Suggestions
        print("\n6. Testing /api/sofia/suggest-times...")
        try:
            response = await client.get(f"{calendar_url}/api/sofia/suggest-times?days=7&limit=3")
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Suggestions: {len(result.get('suggestions', []))}")
        except Exception as e:
            print(f"   ERROR: {e}")

async def test_sofia_function_directly():
    """Test Sofia's calendar function directly"""
    print("\n" + "=" * 60)
    print("Testing Sofia's Calendar Function Directly...")
    print("=" * 60)
    
    try:
        from src.dental.dental_tools import termin_buchen_calendar_system
        from livekit.agents import RunContext
        
        # Mock context (Sofia would provide this)
        class MockContext:
            pass
        
        context = MockContext()
        
        # Test booking through Sofia's function
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print("Testing Sofia's termin_buchen_calendar_system function...")
        result = await termin_buchen_calendar_system(
            context=context,
            patient_name="Sofia Function Test",
            phone="030 88888888",
            appointment_date=tomorrow,
            appointment_time="16:00",
            treatment_type="Sofia Function Test"
        )
        
        print(f"Sofia Function Result: {result}")
        
        if "erfolgreich gebucht" in result:
            print("SUCCESS: Sofia can book appointments through calendar!")
        else:
            print("INFO: Sofia function returned:", result[:100] + "...")
            
    except Exception as e:
        print(f"ERROR testing Sofia function: {e}")
        import traceback
        traceback.print_exc()

async def test_connection_reliability():
    """Test connection under stress"""
    print("\n" + "=" * 60)
    print("Testing Connection Reliability...")
    print("=" * 60)
    
    calendar_url = "http://localhost:3005"
    success_count = 0
    total_tests = 5
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for i in range(total_tests):
            print(f"Connection test {i+1}/{total_tests}...")
            try:
                response = await client.get(f"{calendar_url}/api/sofia/next-available")
                if response.status_code == 200:
                    success_count += 1
                    print(f"   SUCCESS: {response.status_code}")
                else:
                    print(f"   FAILED: {response.status_code}")
            except Exception as e:
                print(f"   ERROR: {e}")
    
    reliability = (success_count / total_tests) * 100
    print(f"\nConnection Reliability: {reliability}% ({success_count}/{total_tests})")
    
    if reliability >= 80:
        print("✅ Connection is RELIABLE")
    else:
        print("❌ Connection needs improvement")

async def main():
    print("SOFIA-CALENDAR CONNECTION TEST")
    print("=" * 60)
    print("Testing ONLY the connection - no changes to Sofia")
    print()
    
    # Test 1: Direct API endpoints
    await test_direct_calendar_endpoints()
    
    # Test 2: Sofia's function
    await test_sofia_function_directly()
    
    # Test 3: Connection reliability
    await test_connection_reliability()
    
    print("\n" + "=" * 60)
    print("CONNECTION TEST COMPLETE")
    print("This test verifies that Sofia can communicate with the calendar")
    print("without making any changes to Sofia itself.")

if __name__ == "__main__":
    asyncio.run(main())