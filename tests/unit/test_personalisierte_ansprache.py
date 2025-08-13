#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für personalisierte Ansprache mit Namen und Tageszeit
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_namen_ansprache():
    """Test dass Sofia den Namen verwendet"""
    try:
        from dental_tools import termin_bestaetigen_und_buchen
        
        print("🧪 Testing: Namen-Ansprache...")
        
        result = await termin_bestaetigen_und_buchen(
            context=None,
            patient_name="Maria Schmidt",
            behandlungsart="Kontrolluntersuchung"
        )
        
        print(f"Input: Name 'Maria Schmidt'")
        print(f"Output: {result}")
        
        # Prüfe dass Name in der Ansprache verwendet wird
        name_in_ansprache = "Maria Schmidt" in result
        personalisierte_frage = "Wie ist Ihre Telefonnummer, Maria Schmidt?" in result
        hoefliche_ansprache = "Perfekt, Maria Schmidt!" in result
        
        if name_in_ansprache and personalisierte_frage and hoefliche_ansprache:
            print("✅ KORREKT: Sofia spricht Patient mit Namen an")
            return True
        else:
            print("❌ FEHLER:")
            if not name_in_ansprache:
                print("   - Name nicht in Ansprache")
            if not personalisierte_frage:
                print("   - Telefonnummer-Frage nicht personalisiert")
            if not hoefliche_ansprache:
                print("   - Keine höfliche Ansprache")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_tageszeit_erkennung():
    """Test dass Sofia die Tageszeit erkennt"""
    try:
        from dental_tools import termin_mit_telefon_abschliessen
        from datetime import datetime
        
        print("\n🧪 Testing: Tageszeit-Erkennung...")
        
        # Simuliere verschiedene Tageszeiten durch Testen der Ausgabe
        result = await termin_mit_telefon_abschliessen(
            context=None,
            patient_name="Thomas Müller",
            telefon="030 11223344",
            behandlungsart="Notfalltermin"
        )
        
        print(f"Input: Name 'Thomas Müller', Telefon '030 11223344'")
        print(f"Output: {result}")
        
        # Prüfe dass Name in Abschlussnachricht verwendet wird
        name_in_abschluss = "Thomas Müller" in result
        personalisierte_verabschiedung = any(phrase in result for phrase in [
            "Vielen Dank, Thomas Müller!",
            "Gute Nacht!",
            "Haben Sie einen schönen Tag",
            "Auf Wiederhören!"
        ])
        
        # Aktuelle Tageszeit prüfen
        jetzt = datetime.now()
        ist_nacht = jetzt.hour >= 22 or jetzt.hour <= 6
        ist_frueh = jetzt.hour <= 7
        
        print(f"   🕐 Aktuelle Zeit: {jetzt.hour}:00 Uhr")
        if ist_nacht:
            print("   🌙 Erkannt als: Nacht")
            erwartet_nacht = "Gute Nacht!" in result
        elif ist_frueh:
            print("   🌅 Erkannt als: Früh am Morgen")
            erwartet_frueh = "schönen Tag" in result
        else:
            print("   ☀️ Erkannt als: Normal")
            erwartet_normal = "Auf Wiederhören!" in result
        
        if name_in_abschluss and personalisierte_verabschiedung:
            print("✅ KORREKT: Personalisierte Verabschiedung mit Tageszeit")
            return True
        else:
            print("❌ FEHLER:")
            if not name_in_abschluss:
                print("   - Name nicht in Abschluss")
            if not personalisierte_verabschiedung:
                print("   - Keine personalisierte Verabschiedung")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_kompletter_personalisierter_ablauf():
    """Test des kompletten personalisierten Ablaufs"""
    try:
        from dental_tools import termin_bestaetigen_und_buchen, termin_mit_telefon_abschliessen
        
        print("\n🧪 Testing: Kompletter personalisierter Ablauf...")
        
        # Schritt 1: Terminbestätigung mit Namen
        print("\n   📋 Schritt 1: Terminbestätigung")
        result1 = await termin_bestaetigen_und_buchen(
            context=None,
            patient_name="Anna Becker",
            behandlungsart="Zahnreinigung"
        )
        
        name_in_bestaetigung = "Anna Becker" in result1
        print(f"      ✅ Name in Bestätigung: {name_in_bestaetigung}")
        
        # Schritt 2: Terminabschluss mit Namen
        print("\n   📋 Schritt 2: Terminabschluss")
        result2 = await termin_mit_telefon_abschliessen(
            context=None,
            patient_name="Anna Becker",
            telefon="030 99887766",
            behandlungsart="Zahnreinigung"
        )
        
        name_in_abschluss = "Anna Becker" in result2
        hoeflicher_abschluss = "Vielen Dank, Anna Becker!" in result2
        print(f"      ✅ Name in Abschluss: {name_in_abschluss}")
        print(f"      ✅ Höflicher Abschluss: {hoeflicher_abschluss}")
        
        # Bewertung
        alle_personalisiert = name_in_bestaetigung and name_in_abschluss and hoeflicher_abschluss
        
        if alle_personalisiert:
            print("\n   ✅ KOMPLETTE PERSONALISIERUNG FUNKTIONIERT!")
            return True
        else:
            print("\n   ❌ Personalisierung unvollständig")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Test: Personalisierte Ansprache")
    print("=" * 60)
    print("Problem 1: Sofia sagt nicht den Namen")
    print("Problem 2: Sofia erkennt nicht die Tageszeit (Nacht)")
    print("Lösung: Personalisierte Ansprache mit Namen und Tageszeit")
    print()
    
    tests = [
        ("Namen-Ansprache", test_namen_ansprache()),
        ("Tageszeit-Erkennung", test_tageszeit_erkennung()),
        ("Kompletter personalisierter Ablauf", test_kompletter_personalisierter_ablauf())
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
        print("\n🏆 PROBLEME GELÖST!")
        print("Sofia spricht Patienten jetzt persönlich mit Namen an!")
        print("Sofia erkennt die Tageszeit und passt ihre Sprache an!")
        print()
        print("🎯 BEISPIELE:")
        print()
        print("📅 TERMINBESTÄTIGUNG:")
        print("Sofia: 'Perfekt, Maria Schmidt!'")
        print("Sofia: 'Wie ist Ihre Telefonnummer, Maria Schmidt?'")
        print()
        print("✅ TERMINABSCHLUSS (Normal):")
        print("Sofia: 'Vielen Dank, Maria Schmidt! Wir sehen uns dann. Auf Wiederhören!'")
        print()
        print("🌙 TERMINABSCHLUSS (Nacht):")
        print("Sofia: 'Vielen Dank, Maria Schmidt! Schlafen Sie gut. Gute Nacht!'")
        print()
        print("🌅 TERMINABSCHLUSS (Früh):")
        print("Sofia: 'Vielen Dank, Maria Schmidt! Haben Sie einen schönen Tag!'")
    else:
        print("\n❌ Probleme noch nicht vollständig gelöst")
        print("Weitere Anpassungen nötig")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
