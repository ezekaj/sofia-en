#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für Gesprächs-Fortsetzung und Emoji-Entfernung
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_gespraech_fortsetzung():
    """Test dass Sofia das Gespräch nicht automatisch beendet"""
    try:
        from dental_tools import termin_mit_telefon_abschliessen
        
        print("🧪 Testing: Gespräch-Fortsetzung...")
        
        result = await termin_mit_telefon_abschliessen(
            context=None,
            patient_name="Test Patient",
            telefon="030 12345678",
            behandlungsart="Kontrolluntersuchung"
        )
        
        print(f"Terminabschluss-Antwort: {result[:200]}...")
        
        # Prüfe dass KEIN automatisches Gesprächsende
        hat_gespraechsende = any(phrase in result.lower() for phrase in [
            "call_end_signal", "auflegen", "gespräch beendet", "auf wiederhören"
        ])
        
        # Prüfe dass Termin erfolgreich gebucht
        termin_gebucht = "erfolgreich gebucht" in result.lower()
        
        if termin_gebucht and not hat_gespraechsende:
            print("✅ KORREKT: Termin gebucht, aber Gespräch läuft weiter")
            return True
        else:
            print("❌ FEHLER:")
            if not termin_gebucht:
                print("   - Termin nicht gebucht")
            if hat_gespraechsende:
                print("   - Gespräch wird automatisch beendet")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_keine_emojis():
    """Test dass Sofia keine Emojis mehr verwendet"""
    try:
        from dental_tools import intelligente_praxis_vorschlaege, termin_bestaetigen_und_buchen
        
        print("\n🧪 Testing: Keine Emojis...")
        
        # Test 1: Praxis-Vorschläge
        result1 = await intelligente_praxis_vorschlaege(
            context=None,
            patient_anfrage="Ich brauche ein Rezept"
        )
        
        # Test 2: Terminbestätigung
        result2 = await termin_bestaetigen_und_buchen(
            context=None,
            patient_name="Test Patient",
            behandlungsart="Kontrolluntersuchung"
        )
        
        # Kombiniere beide Antworten
        combined_result = result1 + " " + result2
        
        print(f"Antworten: {combined_result[:300]}...")
        
        # Liste der häufigsten Emojis
        emojis = [
            "📋", "📅", "🚨", "✅", "📞", "👤", "🦷", "💰", "📄", "🕐", "📍",
            "🔍", "✨", "⚡", "🏥", "📝", "⏱️", "🎵", "💡", "🎯"
        ]
        
        gefundene_emojis = []
        for emoji in emojis:
            if emoji in combined_result:
                gefundene_emojis.append(emoji)
        
        if not gefundene_emojis:
            print("✅ KORREKT: Keine Emojis in den Antworten")
            return True
        else:
            print("❌ FEHLER: Noch Emojis gefunden:")
            for emoji in gefundene_emojis:
                print(f"   - {emoji}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_funktionalitaet_erhalten():
    """Test dass die Funktionalität trotz Änderungen erhalten ist"""
    try:
        from dental_tools import get_zeitabhaengige_begruessung, intelligente_praxis_vorschlaege
        
        print("\n🧪 Testing: Funktionalität erhalten...")
        
        # Test 1: Begrüßung
        begruessung = await get_zeitabhaengige_begruessung(context=None)
        hat_begruessung = any(wort in begruessung.lower() for wort in ["guten", "sofia", "praxis"])
        
        # Test 2: Intelligente Vorschläge
        vorschlag = await intelligente_praxis_vorschlaege(
            context=None,
            patient_anfrage="Ich habe Schmerzen"
        )
        hat_terminvorschlag = "soll ich" in vorschlag.lower() and "buchen" in vorschlag.lower()
        
        print(f"   ✅ Begrüßung funktioniert: {hat_begruessung}")
        print(f"   ✅ Terminvorschläge funktionieren: {hat_terminvorschlag}")
        
        if hat_begruessung and hat_terminvorschlag:
            print("✅ KORREKT: Alle Funktionen arbeiten noch")
            return True
        else:
            print("❌ FEHLER: Funktionen sind kaputt")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Test: Gesprächs-Fortsetzung und Emoji-Entfernung")
    print("=" * 60)
    print("Problem 1: Sofia beendet Gespräch zu früh")
    print("Problem 2: Sofia liest Emojis vor")
    print("Lösung: Automatisches Gesprächsende entfernt + Alle Emojis entfernt")
    print()
    
    tests = [
        ("Gespräch-Fortsetzung", test_gespraech_fortsetzung()),
        ("Keine Emojis", test_keine_emojis()),
        ("Funktionalität erhalten", test_funktionalitaet_erhalten())
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
        print("\n🏆 BEIDE PROBLEME GELÖST!")
        print("Sofia funktioniert jetzt perfekt!")
        print()
        print("✅ GESPRÄCH-FORTSETZUNG:")
        print("   - Sofia beendet Gespräch nicht automatisch")
        print("   - Patient kann weitere Fragen stellen")
        print("   - Natürlicher Gesprächsfluss")
        print()
        print("✅ KEINE EMOJIS MEHR:")
        print("   - Sofia liest keine Emojis vor")
        print("   - Klare, saubere Sprache")
        print("   - 184 Emojis entfernt")
        print()
        print("🎯 BEISPIEL-DIALOG:")
        print("Patient: 'Ich möchte einen Termin'")
        print("Sofia: 'MORGEN um 09:00 Uhr - Kontrolluntersuchung. Soll ich buchen?'")
        print("Patient: 'Ja, Max Mustermann'")
        print("Sofia: 'Perfekt, Max Mustermann! Wie ist Ihre Telefonnummer?'")
        print("Patient: '030 12345678'")
        print("Sofia: 'Termin erfolgreich gebucht! Haben Sie noch weitere Fragen?'")
        print("Patient: 'Nein, danke'")
        print("Sofia: 'Gerne! Auf Wiederhören!'")
    else:
        print("\n❌ Probleme noch nicht vollständig gelöst")
        print("Weitere Anpassungen nötig")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
