import os
from src.dental.dental_tools import kalender_client

print("=== Kalender-Konfiguration ===")
print(f"CALENDAR_URL aus Umgebung: {os.getenv('CALENDAR_URL', 'nicht gesetzt')}")
print(f"Kalender-Client URL: {kalender_client.calendar_url}")
print()

# Prüfe .env Datei
if os.path.exists('.env'):
    print(".env Datei gefunden:")
    with open('.env', 'r') as f:
        for line in f:
            if 'CALENDAR' in line:
                print(f"  {line.strip()}")
else:
    print(".env Datei nicht gefunden!")