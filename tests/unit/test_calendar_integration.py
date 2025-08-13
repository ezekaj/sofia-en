#!/usr/bin/env python3
"""
Test Sofia Calendar Integration
Tests the connection between Sofia agent and the dental calendar
"""

import asyncio
import requests
import json
import time
from datetime import datetime, timedelta

def test_calendar_api():
    """Test if calendar API is accessible"""
    print("🔍 Testing Calendar API...")
    
    try:
        # Test appointments endpoint
        response = requests.get('http://localhost:3005/api/appointments')
        if response.status_code == 200:
            print("✅ Calendar API is accessible")
            appointments = response.json()
            print(f"📅 Found {len(appointments)} appointments")
            return True
        else:
            print(f"❌ Calendar API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Calendar API error: {e}")
        return False

def test_sofia_web_interface():
    """Test if Sofia web interface is running"""
    print("\n🔍 Testing Sofia Web Interface...")
    
    try:
        response = requests.get('http://localhost:5001/')
        if response.status_code == 200:
            print("✅ Sofia web interface is accessible")
            return True
        else:
            print(f"❌ Sofia web interface returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sofia web interface error: {e}")
        return False

def test_livekit_server():
    """Test if LiveKit server is accessible"""
    print("\n🔍 Testing LiveKit Server...")
    
    try:
        # LiveKit doesn't have a simple HTTP endpoint, so we check if port is open
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 7880))
        sock.close()
        
        if result == 0:
            print("✅ LiveKit server port is open")
            return True
        else:
            print("❌ LiveKit server port is closed")
            return False
    except Exception as e:
        print(f"❌ LiveKit server check error: {e}")
        return False

def test_appointment_creation():
    """Test creating appointment via API"""
    print("\n🔍 Testing Appointment Creation...")
    
    try:
        # Create test appointment
        appointment_data = {
            'patient_name': 'Test Patient',
            'phone': '+49 30 12345678',
            'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '14:00',
            'treatment_type': 'Kontrolluntersuchung',
            'notes': 'Test appointment from integration test'
        }
        
        response = requests.post(
            'http://localhost:3005/api/appointments',
            json=appointment_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            print("✅ Appointment created successfully")
            appointment = response.json()
            print(f"📅 Appointment ID: {appointment.get('id', 'N/A')}")
            return appointment.get('id')
        else:
            print(f"❌ Failed to create appointment: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Appointment creation error: {e}")
        return None

def test_sofia_agent_status():
    """Check if Sofia agent is properly configured"""
    print("\n🔍 Checking Sofia Agent Configuration...")
    
    import os
    
    # Check for required files
    files_to_check = [
        'agent.py',
        'clinic_knowledge.py',
        'src/dental/dental_tools.py',
        'dental-calendar/public/sofia-livekit-integration.js'
    ]
    
    all_present = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_present = False
    
    return all_present

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Sofia Calendar Integration Tests")
    print("=" * 50)
    
    results = {
        'calendar_api': test_calendar_api(),
        'sofia_web': test_sofia_web_interface(),
        'livekit': test_livekit_server(),
        'appointment': test_appointment_creation() is not None,
        'agent_files': test_sofia_agent_status()
    }
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test.ljust(20)}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print("\n" + "=" * 50)
    print(f"Total: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Sofia integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the services:")
        print("1. Start calendar: cd dental-calendar && npm start")
        print("2. Start Sofia web: python sofia_web.py")
        print("3. Start LiveKit: docker-compose up livekit")
        print("4. Start Sofia agent: python agent.py dev")

if __name__ == "__main__":
    run_integration_tests()