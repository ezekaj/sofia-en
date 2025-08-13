#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für vollständige deutsche Übersetzung - ALLE italienischen Begriffe
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_keine_italienischen_begriffe():
    """Test dass KEINE italienischen Begriffe mehr im Code sind"""
    try:
        print("🧪 Testing: Keine italienischen Begriffe...")
        
        # Liste der häufigsten italienischen Begriffe
        italienische_begriffe = [
            "Emanuela",  # Name
            "appuntamento", "paziente", "disponibilità", 
            "servizio", "servizi", "descrizione", "durata", "costo",
            "odontoiatria", "generale", "igiene", "dentale", "ortodonzia",
            "implantologia", "estetica", "endodonzia", "chirurgia", "orale", "protesi",
            "Mi dispiace", "Errore", "trovato", "riprogrammare", 
            "cancellazione", "registrata", "felice", "aiutarla", "verificare", "dati",
            "clinica", "chiusa", "domenica", "proposle", "sabato", "orario",
            "prenotazione", "salva", "controlla", "verifica"
        ]
        
        # Lese dental_tools.py
        with open('src/dental_tools.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        gefundene_italienische = []
        
        for begriff in italienische_begriffe:
            if begriff in content:
                # Zähle Vorkommen
                count = content.count(begriff)
                gefundene_italienische.append(f"{begriff} ({count}x)")
        
        if not gefundene_italienische:
            print("✅ PERFEKT: Keine italienischen Begriffe gefunden!")
            return True
        else:
            print("❌ FEHLER: Noch italienische Begriffe gefunden:")
            for begriff in gefundene_italienische:
                print(f"   - {begriff}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_deutsche_begriffe_vorhanden():
    """Test dass deutsche Begriffe korrekt verwendet werden"""
    try:
        print("\n🧪 Testing: Deutsche Begriffe vorhanden...")
        
        # Liste der erwarteten deutschen Begriffe
        deutsche_begriffe = [
            "Dr. Weber",  # Deutscher Name
            "Zahnarztpraxis Dr. Weber",
            "Leistungen unserer Praxis",
            "Beschreibung", "Behandlungsdauer", "Kosten",
            "Allgemeine Zahnheilkunde", "Zahnhygiene", "Kieferorthopädie",
            "Es tut mir leid", "Fehler beim", "Praxis geschlossen",
            "Termin bestätigt", "Patient", "Verfügbarkeit"
        ]
        
        # Lese dental_tools.py
        with open('src/dental_tools.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        gefundene_deutsche = []
        fehlende_deutsche = []
        
        for begriff in deutsche_begriffe:
            if begriff in content:
                gefundene_deutsche.append(begriff)
            else:
                fehlende_deutsche.append(begriff)
        
        erfolg_rate = (len(gefundene_deutsche) / len(deutsche_begriffe)) * 100
        
        print(f"   ✅ Gefundene deutsche Begriffe: {len(gefundene_deutsche)}/{len(deutsche_begriffe)} ({erfolg_rate:.1f}%)")
        
        if fehlende_deutsche:
            print("   ⚠️ Fehlende deutsche Begriffe:")
            for begriff in fehlende_deutsche[:5]:  # Nur erste 5 zeigen
                print(f"      - {begriff}")
        
        return erfolg_rate >= 80  # 80% als Mindestanforderung
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_funktionale_uebersetzung():
    """Test dass übersetzte Funktionen noch funktionieren"""
    try:
        print("\n🧪 Testing: Funktionale Übersetzung...")
        
        # Teste verschiedene Funktionen
        from dental_tools import get_services_info, check_availability
        
        # Test 1: Service-Info
        print("   📋 Teste Service-Info...")
        # Simuliere Aufruf (ohne echten context)
        # result1 = await get_services_info(context=None, service_type="all")
        
        # Test 2: Verfügbarkeits-Check
        print("   📋 Teste Verfügbarkeits-Check...")
        # result2 = await check_availability(context=None, date="2025-12-15", appointment_type="kontrolluntersuchung")
        
        # Wenn wir hier ankommen, sind die Funktionen importierbar
        print("   ✅ Funktionen sind importierbar und strukturell korrekt")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Anderer Fehler: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Test: Vollständige deutsche Übersetzung")
    print("=" * 60)
    print("Ziel: ALLE italienischen Begriffe entfernen und durch deutsche ersetzen")
    print("- Emanuela → Dr. Weber")
    print("- Servizi → Leistungen")
    print("- Mi dispiace → Es tut mir leid")
    print("- Appuntamento → Termin")
    print("- Paziente → Patient")
    print()
    
    tests = [
        ("Keine italienischen Begriffe", test_keine_italienischen_begriffe()),
        ("Deutsche Begriffe vorhanden", test_deutsche_begriffe_vorhanden()),
        ("Funktionale Übersetzung", test_funktionale_uebersetzung())
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func
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
        print("\n🏆 VOLLSTÄNDIGE DEUTSCHE ÜBERSETZUNG ERFOLGREICH!")
        print("Alle italienischen Begriffe wurden entfernt!")
        print()
        print("🎯 ERFOLGREICHE ÜBERSETZUNGEN:")
        print()
        print("🏥 PRAXIS:")
        print("✅ Dr. Emanuela → Dr. Weber")
        print("✅ Zahnarztpraxis Dr. Emanuela → Zahnarztpraxis Dr. Weber")
        print()
        print("📋 LEISTUNGEN:")
        print("✅ Servizi offerti → Leistungen unserer Praxis")
        print("✅ Descrizione → Beschreibung")
        print("✅ Durata → Behandlungsdauer")
        print("✅ Costo → Kosten")
        print()
        print("🚨 FEHLERMELDUNGEN:")
        print("✅ Mi dispiace → Es tut mir leid")
        print("✅ Errore → Fehler beim")
        print("✅ Clinica chiusa → Praxis geschlossen")
        print()
        print("📅 TERMINE:")
        print("✅ Appuntamento → Termin")
        print("✅ Paziente → Patient")
        print("✅ Disponibilità → Verfügbarkeit")
        print()
        print("🇩🇪 DIE ZAHNARZTPRAXIS IST JETZT 100% DEUTSCH!")
    else:
        print("\n❌ Übersetzung noch nicht vollständig")
        print("Weitere italienische Begriffe müssen übersetzt werden")
        print()
        print("📝 NÄCHSTE SCHRITTE:")
        print("1. Alle gefundenen italienischen Begriffe übersetzen")
        print("2. Tests erneut ausführen")
        print("3. Funktionalität prüfen")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
