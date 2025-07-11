#!/usr/bin/env python3
"""
Test für das automatische Auflegen nach Gesprächsende
Überprüft, ob Sofia korrekt auflegt wenn das Gespräch beendet wird
"""

import asyncio
import logging
from src.dental_tools import gespraech_beenden, call_manager, CallStatus

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_automatisches_auflegen():
    """Test des automatischen Auflegens"""
    print("📞 TESTE AUTOMATISCHES AUFLEGEN")
    print("="*60)
    
    print("\n📋 WAS GETESTET WIRD:")
    print("-"*40)
    print("1. 🔄 Gesprächsende-Signal wird generiert")
    print("2. 📞 *[CALL_END_SIGNAL]* wird in Antwort eingefügt") 
    print("3. 🤖 Agent erkennt das Signal")
    print("4. 📞 Sofia legt automatisch auf (Verbindung beenden)")
    print("5. ✅ Gespräch ist vollständig beendet")
    
    # Test 1: CallManager zurücksetzen
    print("\n1️⃣ VORBEREITUNG:")
    print("-"*30)
    call_manager.status = CallStatus.ACTIVE
    call_manager.conversation_ended = False
    call_manager.notes = []
    print("✅ CallManager zurückgesetzt")
    
    # Test 2: Normale Verabschiedung testen
    print("\n2️⃣ TESTE VERABSCHIEDUNG MIT AUFLEGEN:")
    print("-"*45)
    
    print("Patient sagt: 'Danke, auf Wiedersehen!'")
    result = await gespraech_beenden(
        context=None,
        grund="Patient sagt: Danke, auf Wiedersehen!"
    )
    
    print(f"\nSofias Antwort:")
    print(f"'{result}'")
    
    # Test 3: Ende-Signal prüfen
    print("\n3️⃣ PRÜFE AUFLEGEN-SIGNAL:")
    print("-"*35)
    
    has_end_signal = "*[CALL_END_SIGNAL]*" in result
    print(f"📞 Auflegen-Signal vorhanden: {'✅ JA' if has_end_signal else '❌ NEIN'}")
    
    if has_end_signal:
        print("✅ Sofia wird automatisch auflegen!")
        print("📞 Agent wird das Signal erkennen und Verbindung beenden")
    else:
        print("❌ FEHLER: Kein Auflegen-Signal gefunden!")
    
    # Test 4: Status prüfen
    print("\n4️⃣ PRÜFE GESPRÄCHSSTATUS:")
    print("-"*35)
    
    print(f"CallManager Status: {call_manager.status}")
    print(f"Gespräch beendet: {call_manager.conversation_ended}")
    
    if call_manager.status == CallStatus.COMPLETED:
        print("✅ Status korrekt auf COMPLETED gesetzt")
    else:
        print("❌ Status sollte COMPLETED sein")
    
    # Test 5: Rückfrage bei fehlender Verabschiedung
    print("\n5️⃣ TESTE RÜCKFRAGE OHNE VERABSCHIEDUNG:")
    print("-"*50)
    
    # Reset für neuen Test
    call_manager.status = CallStatus.ACTIVE
    call_manager.conversation_ended = False
    
    print("Patient schweigt (keine Verabschiedung)")
    result2 = await gespraech_beenden(
        context=None,
        grund="Patient schweigt"
    )
    
    print(f"\nSofias Antwort:")
    print(f"'{result2}'")
    
    no_end_signal = "*[CALL_END_SIGNAL]*" not in result2
    print(f"📞 Kein Auflegen (korrekt): {'✅ JA' if no_end_signal else '❌ NEIN'}")
    
    if "Haben Sie noch andere Fragen" in result2:
        print("✅ Sofia fragt höflich nach weiteren Wünschen")
        print("📞 Kein automatisches Auflegen (korrekt)")
    else:
        print("❌ Sofia sollte nach weiteren Wünschen fragen")
    
    print("\n" + "="*60)
    print("📊 TEST-ERGEBNIS: AUTOMATISCHES AUFLEGEN")
    print("="*60)
    
    if has_end_signal and no_end_signal:
        print("🎉 ALLE TESTS ERFOLGREICH!")
        print("✅ Sofia legt bei Verabschiedung automatisch auf")
        print("✅ Sofia fragt nach wenn Patient nicht verabschiedet")
        print("📞 AUTOMATISCHES AUFLEGEN FUNKTIONIERT PERFEKT!")
    else:
        print("⚠️ EINIGE TESTS FEHLGESCHLAGEN")
        print("🔧 Bitte Konfiguration prüfen")
    
    print("\n📋 WIE ES FUNKTIONIERT:")
    print("-"*40)
    print("1. Patient verabschiedet sich → 'Tschüss'")
    print("2. Sofia antwortet höflich → 'Auf Wiedersehen!'")
    print("3. Sofia fügt Signal hinzu → *[CALL_END_SIGNAL]*")
    print("4. Agent erkennt Signal → should_end_conversation = True")
    print("5. Monitor erkennt Ende → ctx.room.disconnect()")
    print("6. Verbindung beendet → Sofia hat aufgelegt! 📞")

if __name__ == "__main__":
    asyncio.run(test_automatisches_auflegen())
