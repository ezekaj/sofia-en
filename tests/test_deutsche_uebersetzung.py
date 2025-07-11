#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für deutsche Übersetzung - alle italienischen Begriffe auf Deutsch
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_deutsche_namen():
    """Test dass alle Namen deutsch sind"""
    try:
        from dental_tools import get_clinic_info
        
        print("🧪 Testing: Deutsche Namen...")
        
        result = await get_clinic_info(context=None, info_type="general")
        
        print(f"Praxis-Info: {result}")
        
        # Prüfe dass Dr. Weber verwendet wird (nicht Dr. Emanuela)
        hat_weber = "Dr. Weber" in result
        hat_nicht_emanuela = "Emanuela" not in result
        
        if hat_weber and hat_nicht_emanuela:
            print("✅ KORREKT: Deutsche Namen (Dr. Weber statt Dr. Emanuela)")
            return True
        else:
            print("❌ FEHLER:")
            if not hat_weber:
                print("   - Kein Dr. Weber gefunden")
            if not hat_nicht_emanuela:
                print("   - Noch italienische Namen (Emanuela)")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_deutsche_begriffe():
    """Test dass italienische Begriffe übersetzt sind"""
    try:
        from dental_tools import check_availability
        
        print("\n🧪 Testing: Deutsche Begriffe...")
        
        result = await check_availability(
            context=None,
            date="2025-12-15",
            appointment_type="Kontrolluntersuchung"
        )
        
        print(f"Verfügbarkeits-Check: {result}")
        
        # Prüfe dass deutsche Begriffe verwendet werden
        hat_deutsche_begriffe = any(wort in result for wort in [
            "Verfügbarkeit", "verfügbare", "Zeit", "Datum"
        ])
        
        hat_keine_italienischen = not any(wort in result for wort in [
            "disponibilità", "appuntamento", "paziente", "slot"
        ])
        
        if hat_deutsche_begriffe and hat_keine_italienischen:
            print("✅ KORREKT: Deutsche Begriffe (keine italienischen)")
            return True
        else:
            print("❌ FEHLER:")
            if not hat_deutsche_begriffe:
                print("   - Keine deutschen Begriffe gefunden")
            if not hat_keine_italienischen:
                print("   - Noch italienische Begriffe vorhanden")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_deutsche_terminbuchung():
    """Test dass Terminbuchung auf Deutsch ist"""
    try:
        from dental_tools import schedule_appointment
        
        print("\n🧪 Testing: Deutsche Terminbuchung...")
        
        result = await schedule_appointment(
            context=None,
            patient_name="Max Mustermann",
            phone="030 12345678",
            date="2025-12-20",
            time="10:00",
            appointment_type="kontrolluntersuchung",
            notes="Test"
        )
        
        print(f"Terminbuchung: {result[:200]}...")
        
        # Prüfe dass deutsche Begriffe verwendet werden
        hat_deutsche_bestaetigung = any(wort in result for wort in [
            "Termin bestätigt", "Patient", "Datum", "Zeit"
        ])
        
        hat_keine_italienischen = not any(wort in result for wort in [
            "Appuntamento", "paziente", "confermato"
        ])
        
        if hat_deutsche_bestaetigung and hat_keine_italienischen:
            print("✅ KORREKT: Deutsche Terminbuchung")
            return True
        else:
            print("❌ FEHLER:")
            if not hat_deutsche_bestaetigung:
                print("   - Keine deutsche Bestätigung")
            if not hat_keine_italienischen:
                print("   - Noch italienische Begriffe")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Test: Deutsche Übersetzung")
    print("=" * 60)
    print("Ziel: ALLE italienischen Begriffe auf Deutsch übersetzen")
    print("- Dr. Emanuela → Dr. Weber")
    print("- Appuntamento → Termin")
    print("- Paziente → Patient")
    print("- Disponibilità → Verfügbarkeit")
    print()
    
    tests = [
        ("Deutsche Namen", test_deutsche_namen()),
        ("Deutsche Begriffe", test_deutsche_begriffe()),
        ("Deutsche Terminbuchung", test_deutsche_terminbuchung())
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ZUSAMMENFASSUNG:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n🎯 GESAMT: {passed}/{total} Tests bestanden ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🏆 DEUTSCHE ÜBERSETZUNG ERFOLGREICH!")
        print("Alle italienischen Begriffe wurden auf Deutsch übersetzt!")
        print()
        print("🎯 BEISPIELE:")
        print()
        print("🏥 PRAXIS:")
        print("Vorher: 'Zahnarztpraxis Dr. Emanuela'")
        print("Nachher: 'Zahnarztpraxis Dr. Weber'")
        print()
        print("📅 TERMINE:")
        print("Vorher: 'Appuntamento confermato!'")
        print("Nachher: 'Termin bestätigt!'")
        print()
        print("👤 PATIENTEN:")
        print("Vorher: 'Paziente: Max Mustermann'")
        print("Nachher: 'Patient: Max Mustermann'")
        print()
        print("🕐 VERFÜGBARKEIT:")
        print("Vorher: 'Disponibilità per 2025-01-15'")
        print("Nachher: 'Verfügbarkeit für 2025-01-15'")
    else:
        print("\n❌ Übersetzung noch nicht vollständig")
        print("Weitere italienische Begriffe müssen übersetzt werden")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
