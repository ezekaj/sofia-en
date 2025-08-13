#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für "fehlender Zahn" Erkennung
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_fehlender_zahn():
    """Test dass 'fehlt ein Zahn' erkannt wird"""
    try:
        from dental_tools import intelligente_terminanfrage
        
        print("🧪 Testing: Fehlender Zahn Erkennung...")
        
        test_cases = [
            "Mir fehlt ein Zahn",
            "Ich habe einen Zahn verloren", 
            "Ein Zahn ist rausgefallen",
            "Mein Zahn ist abgebrochen",
            "Ein Zahn ist weg"
        ]
        
        erfolg_count = 0
        
        for test_case in test_cases:
            print(f"\n   📋 Teste: '{test_case}'")
            
            result = await intelligente_terminanfrage(
                context=None,
                patient_anfrage=test_case
            )
            
            # Prüfe dass NICHT nach Grund gefragt wird
            fragt_nach_grund = "worum geht es denn" in result.lower()
            hat_terminvorschlag = "soll ich" in result.lower() and "buchen" in result.lower()
            hat_zahn_emoji = "🦷" in result
            
            if not fragt_nach_grund and hat_terminvorschlag and hat_zahn_emoji:
                print(f"      ✅ ERKANNT: Direkter Terminvorschlag für fehlenden Zahn")
                erfolg_count += 1
            else:
                print(f"      ❌ NICHT ERKANNT:")
                if fragt_nach_grund:
                    print(f"         - Fragt unnötig nach Grund")
                if not hat_terminvorschlag:
                    print(f"         - Kein Terminvorschlag")
                if not hat_zahn_emoji:
                    print(f"         - Kein Zahn-Emoji")
                print(f"         - Antwort: {result}")
        
        erfolg_rate = (erfolg_count / len(test_cases)) * 100
        print(f"\n📊 Erfolgsrate: {erfolg_count}/{len(test_cases)} ({erfolg_rate:.1f}%)")
        
        return erfolg_rate >= 100
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_verstehe_terminmotiv():
    """Test die verstehe_terminmotiv Funktion"""
    try:
        from dental_tools import verstehe_terminmotiv
        
        print("\n🧪 Testing: verstehe_terminmotiv für fehlenden Zahn...")
        
        result = await verstehe_terminmotiv(
            context=None,
            patient_aussage="Mir fehlt ein Zahn"
        )
        
        print(f"Antwort: {result}")
        
        hat_terminvorschlag = "soll ich" in result.lower() and "buchen" in result.lower()
        hat_zahn_emoji = "🦷" in result
        fragt_nicht = "worum geht es denn" not in result.lower()
        
        if hat_terminvorschlag and hat_zahn_emoji and fragt_nicht:
            print("✅ verstehe_terminmotiv erkennt fehlenden Zahn korrekt")
            return True
        else:
            print("❌ verstehe_terminmotiv erkennt fehlenden Zahn nicht")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Test: Fehlender Zahn Erkennung")
    print("=" * 50)
    print("Problem: Sofia geht weg wenn Patient sagt 'fehlt ein Zahn'")
    print("Lösung: Erweiterte Grund-Erkennung für fehlende Zähne")
    print()
    
    test1 = await test_fehlender_zahn()
    test2 = await test_verstehe_terminmotiv()
    
    if test1 and test2:
        print("\n✅ PROBLEM GELÖST!")
        print("Sofia erkennt jetzt 'fehlende Zähne' als Termingrund")
        print("Sie wird nicht mehr weggehen, sondern einen Termin vorschlagen")
        print()
        print("🦷 Erkannte Begriffe:")
        print("• fehlt, fehlend")
        print("• verloren, rausgefallen") 
        print("• abgebrochen, weg")
        print()
        print("📅 Sofia wird antworten:")
        print("'🦷 MORGEN um 09:00 Uhr - Fehlender Zahn/Zahnersatz. Soll ich buchen?'")
    else:
        print("\n❌ Problem noch nicht vollständig gelöst")
        print("Weitere Anpassungen nötig")
    
    return test1 and test2

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
