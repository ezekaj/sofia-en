#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für Wiederherstellung der Begrüßungsfunktionen
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_zeitabhaengige_begruessung():
    """Test dass die zeitabhängige Begrüßung funktioniert"""
    try:
        from dental_tools import get_zeitabhaengige_begruessung
        from datetime import datetime
        
        print("🧪 Testing: Zeitabhängige Begrüßung...")
        
        result = await get_zeitabhaengige_begruessung(context=None)
        
        print(f"Begrüßung: {result}")
        
        # Prüfe dass eine Begrüßung enthalten ist
        jetzt = datetime.now()
        
        if 6 <= jetzt.hour < 12:
            erwartet = "Guten Morgen"
        elif 12 <= jetzt.hour < 18:
            erwartet = "Guten Tag"
        else:
            erwartet = "Guten Abend"
        
        hat_begruessung = erwartet.lower() in result.lower()
        hat_sofia = "sofia" in result.lower()
        hat_praxis = "praxis" in result.lower() or "zahnarzt" in result.lower()
        
        print(f"   🕐 Aktuelle Zeit: {jetzt.hour}:00 Uhr")
        print(f"   📝 Erwartet: {erwartet}")
        print(f"   ✅ Hat Begrüßung: {hat_begruessung}")
        print(f"   ✅ Hat Sofia: {hat_sofia}")
        print(f"   ✅ Hat Praxis: {hat_praxis}")
        
        if hat_begruessung and hat_sofia:
            print("✅ KORREKT: Zeitabhängige Begrüßung funktioniert")
            return True
        else:
            print("❌ FEHLER:")
            if not hat_begruessung:
                print(f"   - Keine {erwartet}-Begrüßung")
            if not hat_sofia:
                print("   - Sofia stellt sich nicht vor")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_sie_anrede():
    """Test dass Sofia 'Sie' verwendet"""
    try:
        from dental_tools import telefonnummer_erfragen
        
        print("\n🧪 Testing: 'Sie' Anrede...")
        
        result = await telefonnummer_erfragen(context=None)
        
        print(f"Telefonnummer-Frage: {result}")
        
        # Prüfe dass "Sie" verwendet wird
        hat_sie = "ihre" in result.lower()
        hat_nicht_du = "deine" not in result.lower()
        
        if hat_sie and hat_nicht_du:
            print("✅ KORREKT: Sofia verwendet höfliches 'Sie'")
            return True
        else:
            print("❌ FEHLER:")
            if not hat_sie:
                print("   - Verwendet nicht 'Ihre'")
            if not hat_nicht_du:
                print("   - Verwendet 'deine' statt 'Ihre'")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_komplette_begruessung_workflow():
    """Test des kompletten Begrüßungsworkflows"""
    try:
        from dental_tools import get_zeitabhaengige_begruessung, intelligente_praxis_vorschlaege
        
        print("\n🧪 Testing: Kompletter Begrüßungsworkflow...")
        
        # Schritt 1: Begrüßung
        print("\n   📋 Schritt 1: Begrüßung")
        begruessung = await get_zeitabhaengige_begruessung(context=None)
        
        hat_begruessung = any(wort in begruessung.lower() for wort in ["guten morgen", "guten tag", "guten abend"])
        print(f"      ✅ Zeitabhängige Begrüßung: {hat_begruessung}")
        
        # Schritt 2: Patientenanfrage
        print("\n   📋 Schritt 2: Patientenanfrage")
        anfrage = await intelligente_praxis_vorschlaege(
            context=None,
            patient_anfrage="Ich habe Schmerzen"
        )
        
        hat_terminvorschlag = "soll ich" in anfrage.lower() and "buchen" in anfrage.lower()
        print(f"      ✅ Intelligenter Terminvorschlag: {hat_terminvorschlag}")
        
        # Bewertung
        workflow_ok = hat_begruessung and hat_terminvorschlag
        
        if workflow_ok:
            print("\n   ✅ KOMPLETTER WORKFLOW FUNKTIONIERT!")
            print(f"      1. Begrüßung: {begruessung[:50]}...")
            print(f"      2. Terminvorschlag: {anfrage[:50]}...")
            return True
        else:
            print("\n   ❌ Workflow hat Probleme")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Test: Begrüßung Wiederherstellung")
    print("=" * 60)
    print("Problem 1: Sofia sagt nicht mehr 'Guten Morgen'")
    print("Problem 2: Sofia soll 'Sie' verwenden (nicht 'du')")
    print("Lösung: Ursprüngliche Funktionen wiederherstellen")
    print()
    
    tests = [
        ("Zeitabhängige Begrüßung", test_zeitabhaengige_begruessung()),
        ("'Sie' Anrede", test_sie_anrede()),
        ("Kompletter Begrüßungsworkflow", test_komplette_begruessung_workflow())
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
        print("\n🏆 FUNKTIONEN WIEDERHERGESTELLT!")
        print("Sofia begrüßt wieder zeitabhängig und verwendet 'Sie'!")
        print()
        print("🎯 BEISPIELE:")
        print()
        print("🌅 MORGENS (6-12 Uhr):")
        print("Sofia: 'Guten Morgen! Hier ist Sofia von der Zahnarztpraxis Dr. Emanuela.'")
        print()
        print("☀️ TAGSÜBER (12-18 Uhr):")
        print("Sofia: 'Guten Tag! Hier ist Sofia von der Zahnarztpraxis Dr. Emanuela.'")
        print()
        print("🌆 ABENDS (18-22 Uhr):")
        print("Sofia: 'Guten Abend! Hier ist Sofia von der Zahnarztpraxis Dr. Emanuela.'")
        print()
        print("📞 HÖFLICHE ANREDE:")
        print("Sofia: 'Wie ist Ihre Telefonnummer?' (nicht 'deine')")
    else:
        print("\n❌ Funktionen noch nicht vollständig wiederhergestellt")
        print("Weitere Anpassungen nötig")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
