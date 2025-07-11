#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für intelligente Praxis-Vorschläge
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_rezept_anfragen():
    """Test für Rezept-Anfragen"""
    try:
        from dental_tools import intelligente_praxis_vorschlaege
        
        print("🧪 Testing: Rezept-Anfragen...")
        
        test_cases = [
            "Ich brauche ein Rezept",
            "Ich möchte ein Medikament",
            "Können Sie mir Schmerzmittel verschreiben?",
            "Ich brauche Antibiotika",
            "Ich hätte gerne Tabletten"
        ]
        
        erfolg_count = 0
        
        for test_case in test_cases:
            print(f"\n   📋 Teste: '{test_case}'")
            
            result = await intelligente_praxis_vorschlaege(
                context=None,
                patient_anfrage=test_case
            )
            
            # Prüfe dass Praxisbesuch vorgeschlagen wird
            hat_praxisbesuch = "kommen sie" in result.lower() and "vorbei" in result.lower()
            hat_oeffnungszeiten = "öffnungszeiten" in result.lower()
            kein_termin_noetig = "kein termin" in result.lower()
            
            if hat_praxisbesuch and hat_oeffnungszeiten:
                print(f"      ✅ KORREKT: Praxisbesuch vorgeschlagen")
                erfolg_count += 1
            else:
                print(f"      ❌ FEHLER: Kein Praxisbesuch vorgeschlagen")
                print(f"         Antwort: {result}")
        
        erfolg_rate = (erfolg_count / len(test_cases)) * 100
        print(f"\n📊 Rezept-Anfragen: {erfolg_count}/{len(test_cases)} ({erfolg_rate:.1f}%)")
        
        return erfolg_rate >= 100
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_ueberweisungs_anfragen():
    """Test für Überweisungs-Anfragen"""
    try:
        from dental_tools import intelligente_praxis_vorschlaege
        
        print("\n🧪 Testing: Überweisungs-Anfragen...")
        
        test_cases = [
            "Ich brauche eine Überweisung",
            "Können Sie mich überweisen?",
            "Ich muss zum Kieferorthopäden",
            "Ich brauche einen Spezialisten",
            "Überweisung zum Chirurgen bitte"
        ]
        
        erfolg_count = 0
        
        for test_case in test_cases:
            print(f"\n   📋 Teste: '{test_case}'")
            
            result = await intelligente_praxis_vorschlaege(
                context=None,
                patient_anfrage=test_case
            )
            
            # Prüfe dass Praxisbesuch vorgeschlagen wird
            hat_praxisbesuch = "kommen sie" in result.lower() and "vorbei" in result.lower()
            hat_schnell = "5 minuten" in result.lower() or "sofort" in result.lower()
            
            if hat_praxisbesuch and hat_schnell:
                print(f"      ✅ KORREKT: Schneller Praxisbesuch vorgeschlagen")
                erfolg_count += 1
            else:
                print(f"      ❌ FEHLER: Kein passender Vorschlag")
                print(f"         Antwort: {result}")
        
        erfolg_rate = (erfolg_count / len(test_cases)) * 100
        print(f"\n📊 Überweisungs-Anfragen: {erfolg_count}/{len(test_cases)} ({erfolg_rate:.1f}%)")
        
        return erfolg_rate >= 100
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_befund_anfragen():
    """Test für Befund/Röntgenbild-Anfragen"""
    try:
        from dental_tools import intelligente_praxis_vorschlaege
        
        print("\n🧪 Testing: Befund-Anfragen...")
        
        test_cases = [
            "Ich möchte meinen Befund abholen",
            "Ist mein Röntgenbild fertig?",
            "Ich brauche meine Aufnahme",
            "Können Sie mir das Ergebnis geben?",
            "Ich hole mein Bild ab"
        ]
        
        erfolg_count = 0
        
        for test_case in test_cases:
            print(f"\n   📋 Teste: '{test_case}'")
            
            result = await intelligente_praxis_vorschlaege(
                context=None,
                patient_anfrage=test_case
            )
            
            # Prüfe dass Abholung vorgeschlagen wird
            hat_abholung = "abholen" in result.lower() or "bereit" in result.lower()
            hat_praxisbesuch = "kommen sie" in result.lower()
            
            if hat_abholung and hat_praxisbesuch:
                print(f"      ✅ KORREKT: Abholung vorgeschlagen")
                erfolg_count += 1
            else:
                print(f"      ❌ FEHLER: Keine Abholung vorgeschlagen")
                print(f"         Antwort: {result}")
        
        erfolg_rate = (erfolg_count / len(test_cases)) * 100
        print(f"\n📊 Befund-Anfragen: {erfolg_count}/{len(test_cases)} ({erfolg_rate:.1f}%)")
        
        return erfolg_rate >= 100
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_normale_termine():
    """Test dass normale Terminanfragen noch funktionieren"""
    try:
        from dental_tools import intelligente_praxis_vorschlaege
        
        print("\n🧪 Testing: Normale Terminanfragen...")
        
        test_cases = [
            "Ich habe Schmerzen",
            "Ich brauche eine Kontrolle",
            "Ich möchte eine Zahnreinigung"
        ]
        
        erfolg_count = 0
        
        for test_case in test_cases:
            print(f"\n   📋 Teste: '{test_case}'")
            
            result = await intelligente_praxis_vorschlaege(
                context=None,
                patient_anfrage=test_case
            )
            
            # Prüfe dass Terminvorschlag gemacht wird
            hat_terminvorschlag = "soll ich" in result.lower() and "buchen" in result.lower()
            hat_uhrzeit = any(zeit in result for zeit in ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"])
            
            if hat_terminvorschlag and hat_uhrzeit:
                print(f"      ✅ KORREKT: Terminvorschlag gemacht")
                erfolg_count += 1
            else:
                print(f"      ❌ FEHLER: Kein Terminvorschlag")
                print(f"         Antwort: {result}")
        
        erfolg_rate = (erfolg_count / len(test_cases)) * 100
        print(f"\n📊 Normale Termine: {erfolg_count}/{len(test_cases)} ({erfolg_rate:.1f}%)")
        
        return erfolg_rate >= 100
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Test: Intelligente Praxis-Vorschläge")
    print("=" * 60)
    print("Sofia soll intelligent unterscheiden:")
    print("• Rezept → Praxisbesuch")
    print("• Überweisung → Praxisbesuch") 
    print("• Befund → Abholung")
    print("• Termine → Terminbuchung")
    print()
    
    tests = [
        ("Rezept-Anfragen", test_rezept_anfragen()),
        ("Überweisungs-Anfragen", test_ueberweisungs_anfragen()),
        ("Befund-Anfragen", test_befund_anfragen()),
        ("Normale Termine", test_normale_termine())
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
        print("\n🏆 EXZELLENT: Sofia ist jetzt super-intelligent!")
        print("✅ Rezept → 'Kommen Sie vorbei!'")
        print("✅ Überweisung → 'Dauert nur 5 Minuten!'")
        print("✅ Befund → 'Bereit zur Abholung!'")
        print("✅ Termine → Automatische Buchung")
        print("\n🎯 BEISPIELE:")
        print("Patient: 'Ich brauche ein Rezept'")
        print("Sofia: 'Kommen Sie einfach vorbei - kein Termin nötig!'")
        print()
        print("Patient: 'Ich habe Schmerzen'")
        print("Sofia: '🚨 MORGEN um 09:00 Uhr - Notfall. Soll ich buchen?'")
    else:
        print("\n🥈 VERBESSERUNG NÖTIG: Einige intelligente Vorschläge funktionieren noch nicht")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
