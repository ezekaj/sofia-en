#!/usr/bin/env python3
"""
Test der Kalender-Verbindung
"""
import requests
import json
from datetime import datetime, timedelta

# Kalender URL
CALENDAR_URL = "http://localhost:3005"

print("=== Teste Kalender-Verbindung ===")
print(f"Kalender URL: {CALENDAR_URL}")
print()

# Test 1: Health Check
print("1. Health Check...")
try:
    response = requests.get(f"{CALENDAR_URL}/", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Kalender erreichbar!")
    else:
        print("   ❌ Kalender antwortet mit Fehler")
except Exception as e:
    print(f"   ❌ Fehler: {e}")

print()

# Test 2: Sofia API Endpoints
print("2. Teste Sofia API Endpoints...")
endpoints = [
    "/api/sofia/next-available",
    "/api/sofia/today",
    "/api/sofia/week"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{CALENDAR_URL}{endpoint}", timeout=5)
        print(f"   {endpoint}: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"      Response: {json.dumps(data, indent=2)[:100]}...")
    except Exception as e:
        print(f"   {endpoint}: ❌ Fehler - {e}")

print()

# Test 3: Termin buchen
print("3. Teste Terminbuchung...")
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
booking_data = {
    "patientName": "Test Patient",
    "patientPhone": "030 12345678",
    "requestedDate": tomorrow,
    "requestedTime": "10:00",
    "treatmentType": "Kontrolluntersuchung"
}

print(f"   Buchungsdaten: {json.dumps(booking_data, indent=2)}")

try:
    response = requests.post(
        f"{CALENDAR_URL}/api/sofia/appointment",
        json=booking_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        print("   ✅ Terminbuchung erfolgreich!")
    else:
        print("   ❌ Terminbuchung fehlgeschlagen")
        
except Exception as e:
    print(f"   ❌ Fehler bei Buchung: {e}")

print()

# Test 4: Alle Termine abrufen
print("4. Alle Termine abrufen...")
try:
    response = requests.get(f"{CALENDAR_URL}/api/appointments", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        appointments = response.json()
        print(f"   Anzahl Termine: {len(appointments)}")
        for apt in appointments[:3]:  # Zeige erste 3
            print(f"   - {apt.get('title', 'Kein Titel')}")
except Exception as e:
    print(f"   ❌ Fehler: {e}")

print("\n=== Test abgeschlossen ===")