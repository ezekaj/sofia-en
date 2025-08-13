#!/usr/bin/env python3
"""
Final Sofia-Calendar Connection Report
Demonstrates that Sofia can successfully connect to and interact with the calendar
"""
import asyncio
import httpx
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def generate_connection_report():
    print("SOFIA-CALENDAR CONNECTION FINAL REPORT")
    print("=" * 60)
    print("Testing ONLY the connection between Sofia and Calendar")
    print("No modifications to Sofia - pure connectivity test")
    print()
    
    calendar_url = "http://localhost:3005"
    results = {}
    
    # Test 1: Basic Health Check
    print("TEST 1: Calendar Service Health")
    print("-" * 30)
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{calendar_url}/health")
            health_data = response.json()
            results['health'] = True
            print(f"Status: HEALTHY")
            print(f"Response: {health_data}")
        except Exception as e:
            results['health'] = False
            print(f"Status: FAILED - {e}")
    
    print()
    
    # Test 2: Sofia's Primary Endpoints
    print("TEST 2: Sofia's Calendar Endpoints")
    print("-" * 30)
    endpoints = [
        ("/api/sofia/next-available", "GET", "Next available appointment"),
        ("/api/sofia/today", "GET", "Today's appointments"),
        ("/api/sofia/suggest-times?days=7&limit=3", "GET", "Appointment suggestions")
    ]
    
    results['endpoints'] = {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint, method, description in endpoints:
            try:
                response = await client.get(f"{calendar_url}{endpoint}")
                data = response.json()
                results['endpoints'][endpoint] = True
                print(f"✓ {description}: SUCCESS")
                print(f"  Response: {str(data)[:60]}...")
            except Exception as e:
                results['endpoints'][endpoint] = False
                print(f"✗ {description}: FAILED - {e}")
    
    print()
    
    # Test 3: Appointment Booking (Core Function)
    print("TEST 3: Appointment Booking")
    print("-" * 30)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    booking_data = {
        "patientName": "Sofia Connection Test",
        "patientPhone": "+49 30 12345678",
        "requestedDate": tomorrow,
        "requestedTime": "16:00",
        "treatmentType": "Connection Test"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(f"{calendar_url}/api/sofia/appointment", json=booking_data)
            booking_result = response.json()
            results['booking'] = booking_result.get('success', False)
            
            if results['booking']:
                print("✓ Appointment Booking: SUCCESS")
                print(f"  Message: {booking_result.get('message')}")
                if booking_result.get('appointment'):
                    apt = booking_result['appointment']
                    print(f"  Appointment ID: {apt.get('id')}")
                    print(f"  Date/Time: {apt.get('date')} {apt.get('time')}")
            else:
                print("✗ Appointment Booking: FAILED")
                print(f"  Message: {booking_result.get('message')}")
                results['booking'] = False
        except Exception as e:
            results['booking'] = False
            print(f"✗ Appointment Booking: ERROR - {e}")
    
    print()
    
    # Test 4: Sofia's Function Direct Test
    print("TEST 4: Sofia's Function Integration")
    print("-" * 30)
    try:
        from src.dental.dental_tools import termin_buchen_calendar_system
        
        # Mock context (Sofia provides this during actual operation)
        class MockContext:
            pass
        
        context = MockContext()
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Test Sofia's actual function
        sofia_result = await termin_buchen_calendar_system(
            context=context,
            patient_name="Sofia Function Test",
            phone="030 77777777",
            appointment_date=tomorrow,
            appointment_time="17:00",
            treatment_type="Sofia Integration Test"
        )
        
        # Check if booking was successful
        if "erfolgreich gebucht" in sofia_result or "successfully" in sofia_result.lower():
            results['sofia_function'] = True
            print("✓ Sofia Function: SUCCESS")
            print("  Sofia can successfully call calendar and book appointments")
        else:
            results['sofia_function'] = False
            print("✗ Sofia Function: NEEDS ATTENTION")
            print(f"  Result: {sofia_result[:100]}...")
            
    except Exception as e:
        results['sofia_function'] = False
        print(f"✗ Sofia Function: ERROR - {e}")
    
    print()
    
    # Test 5: Connection Stability
    print("TEST 5: Connection Stability")
    print("-" * 30)
    success_count = 0
    total_tests = 5
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for i in range(total_tests):
            try:
                response = await client.get(f"{calendar_url}/api/sofia/next-available")
                if response.status_code == 200:
                    success_count += 1
            except:
                pass
    
    stability = (success_count / total_tests) * 100
    results['stability'] = stability
    print(f"Connection Stability: {stability}% ({success_count}/{total_tests})")
    
    if stability >= 80:
        print("✓ Connection is STABLE")
    else:
        print("✗ Connection needs improvement")
    
    print()
    
    # Final Summary
    print("FINAL CONNECTION SUMMARY")
    print("=" * 60)
    
    checks = [
        ("Calendar Health", results.get('health', False)),
        ("Sofia Endpoints", all(results.get('endpoints', {}).values())),
        ("Appointment Booking", results.get('booking', False)),
        ("Sofia Function", results.get('sofia_function', False)),
        ("Connection Stability", results.get('stability', 0) >= 80)
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    print(f"Connection Tests: {passed}/{total} PASSED")
    print()
    
    for test_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    print()
    
    if passed == total:
        print("🎉 SUCCESS: Sofia-Calendar connection is FULLY WORKING!")
        print("✓ Sofia can successfully communicate with the calendar")
        print("✓ All appointment booking functions are operational")
        print("✓ Connection is stable and reliable")
        print()
        print("CONNECTIVITY STATUS: READY FOR PRODUCTION")
    else:
        print("⚠️  PARTIAL SUCCESS: Some connections need attention")
        print(f"Working: {passed}/{total} components")
        print()
        print("CONNECTIVITY STATUS: NEEDS REVIEW")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(generate_connection_report())