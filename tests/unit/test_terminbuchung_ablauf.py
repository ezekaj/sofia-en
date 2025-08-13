#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für korrekten Terminbuchungsablauf
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_terminbestaetigung_mit_name():
    """Test dass Sofia nach Telefonnummer fragt wenn Name gegeben wird"""
    try:
        from dental_tools import termin_bestaetigen_und_buchen
        
        print("🧪 Testing: Terminbestätigung mit Name...")
        
        result = await termin_bestaetigen_und_buchen(
            context=None,
            patient_name="Max Mustermann",
            behandlungsart="Kontrolluntersuchung"
        )
        
        print(f"Input: Name 'Max Mustermann' gegeben")
        print(f"Output: {result}")
        
        # Prüfe dass nach Telefonnummer gefragt wird
        fragt_nach_telefon = "wie ist ihre telefonnummer" in result.lower()
        hat_terminbestaetigung = "termin bestätigt" in result.lower()
        hat_patient_name = "Max Mustermann" in result
        
        if fragt_nach_telefon and hat_terminbestaetigung and hat_patient_name:
            print("✅ KORREKT: Termin bestätigt und nach Telefonnummer gefragt")
            return True
        else:
            print("❌ FEHLER:")
            if not fragt_nach_telefon:
                print("   - Fragt nicht nach Telefonnummer")
            if not hat_terminbestaetigung:
                print("   - Keine Terminbestätigung")
            if not hat_patient_name:
                print("   - Name nicht in Antwort")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_terminabschluss_mit_telefon():
    """Test dass Sofia Termin abschließt wenn Telefonnummer gegeben wird"""
    try:
        from dental_tools import termin_mit_telefon_abschliessen
        
        print("\n🧪 Testing: Terminabschluss mit Telefonnummer...")
        
        result = await termin_mit_telefon_abschliessen(
            context=None,
            patient_name="Max Mustermann",
            telefon="030 12345678",
            behandlungsart="Kontrolluntersuchung"
        )
        
        print(f"Input: Name 'Max Mustermann', Telefon '030 12345678'")
        print(f"Output: {result}")
        
        # Prüfe dass Termin gebucht wird
        termin_gebucht = "erfolgreich gebucht" in result.lower()
        hat_patient_name = "Max Mustermann" in result
        hat_telefon = "030 12345678" in result
        hat_abschied = "auf wiederhören" in result.lower()
        
        if termin_gebucht and hat_patient_name and hat_telefon and hat_abschied:
            print("✅ KORREKT: Termin gebucht und Gespräch beendet")
            return True
        else:
            print("❌ FEHLER:")
            if not termin_gebucht:
                print("   - Termin nicht gebucht")
            if not hat_patient_name:
                print("   - Name fehlt")
            if not hat_telefon:
                print("   - Telefonnummer fehlt")
            if not hat_abschied:
                print("   - Kein Abschied")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_kompletter_buchungsablauf():
    """Test des kompletten Buchungsablaufs"""
    try:
        from dental_tools import intelligente_praxis_vorschlaege, termin_bestaetigen_und_buchen, termin_mit_telefon_abschliessen
        
        print("\n🧪 Testing: Kompletter Buchungsablauf...")
        
        # Schritt 1: Patient sagt "Ich habe Schmerzen"
        print("\n   📋 Schritt 1: Patient sagt 'Ich habe Schmerzen'")
        result1 = await intelligente_praxis_vorschlaege(
            context=None,
            patient_anfrage="Ich habe Schmerzen"
        )
        
        hat_terminvorschlag = "soll ich" in result1.lower() and "buchen" in result1.lower()
        print(f"      ✅ Terminvorschlag: {hat_terminvorschlag}")
        
        # Schritt 2: Patient sagt "Ja" und gibt Namen
        print("\n   📋 Schritt 2: Patient bestätigt und gibt Namen")
        result2 = await termin_bestaetigen_und_buchen(
            context=None,
            patient_name="Anna Schmidt",
            behandlungsart="Notfalltermin"
        )
        
        fragt_nach_telefon = "wie ist ihre telefonnummer" in result2.lower()
        print(f"      ✅ Fragt nach Telefonnummer: {fragt_nach_telefon}")
        
        # Schritt 3: Patient gibt Telefonnummer
        print("\n   📋 Schritt 3: Patient gibt Telefonnummer")
        result3 = await termin_mit_telefon_abschliessen(
            context=None,
            patient_name="Anna Schmidt",
            telefon="030 98765432",
            behandlungsart="Notfalltermin"
        )
        
        termin_gebucht = "erfolgreich gebucht" in result3.lower()
        print(f"      ✅ Termin gebucht: {termin_gebucht}")
        
        # Bewertung
        alle_schritte_ok = hat_terminvorschlag and fragt_nach_telefon and termin_gebucht
        
        if alle_schritte_ok:
            print("\n   ✅ KOMPLETTER ABLAUF FUNKTIONIERT!")
            return True
        else:
            print("\n   ❌ Ablauf hat Probleme")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Test: Terminbuchungsablauf")
    print("=" * 60)
    print("Problem: Sofia fragt nicht nach Telefonnummer wenn Name gegeben wird")
    print("Lösung: Neue Funktionen für korrekten Buchungsablauf")
    print()
    
    tests = [
        ("Terminbestätigung mit Name", test_terminbestaetigung_mit_name()),
        ("Terminabschluss mit Telefon", test_terminabschluss_mit_telefon()),
        ("Kompletter Buchungsablauf", test_kompletter_buchungsablauf())
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
        print("\n🏆 PROBLEM GELÖST!")
        print("Sofia fragt jetzt automatisch nach der Telefonnummer!")
        print()
        print("🎯 KORREKTER ABLAUF:")
        print("1. Patient: 'Ich habe Schmerzen'")
        print("2. Sofia: 'MORGEN um 09:00 Uhr - Notfall. Soll ich buchen?'")
        print("3. Patient: 'Ja, Max Mustermann'")
        print("4. Sofia: 'Termin bestätigt für Max Mustermann. Wie ist Ihre Telefonnummer?'")
        print("5. Patient: '030 12345678'")
        print("6. Sofia: 'Termin gebucht! Auf Wiederhören!' [legt auf]")
    else:
        print("\n❌ Problem noch nicht vollständig gelöst")
        print("Weitere Anpassungen nötig")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
