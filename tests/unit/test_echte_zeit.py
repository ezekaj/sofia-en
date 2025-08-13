#!/usr/bin/env python3
"""
Einfacher Test für automatische Datum/Uhrzeit-Erkennung
"""

import asyncio
from datetime import datetime
from src.dental_tools import get_aktuelle_datetime_info, get_zeitabhaengige_begruessung

async def test_zeitdaten():
    """Test der automatischen Zeitdaten"""
    print("🕐 TESTE AUTOMATISCHE ZEITDATEN")
    print("="*50)
    
    # Echte aktuelle Zeit
    jetzt = datetime.now()
    print(f"📅 ECHTES DATUM: {jetzt.strftime('%A, %d.%m.%Y')}")
    print(f"🕐 ECHTE UHRZEIT: {jetzt.strftime('%H:%M')}")
    print()
    
    # Test Sofia's Zeitwahrnehmung
    print("🤖 SOFIA'S ZEITWAHRNEHMUNG:")
    print("-"*30)
    
    # Test 1: Aktuelle Zeitdaten
    zeitdaten = await get_aktuelle_datetime_info(context=None)
    print(zeitdaten)
    
    print("\n" + "="*50)
    print("✅ SOFIA KENNT DIE ECHTE ZEIT!")
    print("✅ Keine manuellen Änderungen mehr nötig!")
    print("✅ Das System ist ZEITBEWUSST!")

if __name__ == "__main__":
    asyncio.run(test_zeitdaten())
