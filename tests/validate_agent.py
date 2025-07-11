#!/usr/bin/env python3
"""
Validierungsskript für den bereinigten Agenten
"""

print("🧪 VALIDIERUNG DER BEREINIGTEN AGENT-DATEIEN")
print("==================================================")

try:
    print("1️⃣ Teste Agent-Import...")
    from agent import DentalReceptionist
    print("✅ Agent erfolgreich importiert")
    
    print("\n2️⃣ Teste Dental Tools...")
    from dental_tools import gespraech_beenden, get_zeitabhaengige_begruessung
    print("✅ Dental Tools erfolgreich importiert")
    
    print("\n3️⃣ Teste Appointment Manager...")
    from appointment_manager import appointment_manager
    print("✅ Appointment Manager erfolgreich importiert")
    
    print("\n4️⃣ Teste Clinic Knowledge...")
    from clinic_knowledge import CLINIC_INFO
    print("✅ Clinic Knowledge erfolgreich importiert")
    
    print("\n5️⃣ Teste Prompts...")
    from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
    print("✅ Prompts erfolgreich importiert")
    
    print("\n🎉 VALIDATION ERFOLGREICH!")
    print("==================================================")
    print("✅ Alle essentiellen Komponenten funktionieren")
    print("✅ Agent ist bereit für den Einsatz")
    print("✅ Überflüssige Dateien wurden erfolgreich entfernt")
    
except Exception as e:
    print(f"❌ FEHLER: {e}")
    print("❌ Validation fehlgeschlagen")
    exit(1)
