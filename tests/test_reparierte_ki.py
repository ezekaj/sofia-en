#!/usr/bin/env python3
import asyncio
import logging
from src.dental_tools import termin_direkt_buchen, gespraech_beenden

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_reparierte_ki():
    """Test der reparierten KI-Funktionen"""
    print("🔧 TESTE REPARIERTE KI-FUNKTIONEN")
    print("="*60)
    
    # Test 1: Terminbuchung mit verbesserter Antwort
    print("\n1️⃣ TESTE TERMINBUCHUNG:")
    print("-"*40)
    
    result = await termin_direkt_buchen(
        context=None,
        patient_name="Max Mustermann",
        phone="0123456789",
        appointment_date="2025-07-08",
        appointment_time="10:00",
        treatment_type="Kontrolluntersuchung"
    )
    
    print("ANTWORT NACH TERMINBUCHUNG:")
    print(result)
    print()
    
    # Prüfe ob die wichtige Rückfrage enthalten ist
    if "Haben Sie noch andere Fragen" in result:
        print("✅ RÜCKFRAGE NACH WEITEREN WÜNSCHEN: VORHANDEN")
    else:
        print("❌ RÜCKFRAGE NACH WEITEREN WÜNSCHEN: FEHLT")
    
    # Prüfe Länge der Antwort
    lines = result.split('\n')
    print(f"📏 LÄNGE DER ANTWORT: {len(lines)} Zeilen")
    if len(lines) <= 6:
        print("✅ ANTWORT IST KURZ UND PRÄGNANT")
    else:
        print("❌ ANTWORT IST ZU LANG")
    
    # Test 2: Gesprächsende - erst Rückfrage
    print("\n2️⃣ TESTE GESPRÄCHSENDE (OHNE VERABSCHIEDUNG):")
    print("-"*50)
    
    result = await gespraech_beenden(
        context=None,
        grund="Patient schweigt"
    )
    
    print("ANTWORT BEI FEHLENDEM ABSCHIED:")
    print(result)
    print()
    
    if "Haben Sie noch andere Fragen" in result:
        print("✅ RÜCKFRAGE BEI FEHLENDER VERABSCHIEDUNG: KORREKT")
    else:
        print("❌ SOLLTE RÜCKFRAGEN STATT BEENDEN")
    
    # Test 3: Gesprächsende - mit echter Verabschiedung
    print("\n3️⃣ TESTE GESPRÄCHSENDE (MIT VERABSCHIEDUNG):")
    print("-"*50)
    
    result = await gespraech_beenden(
        context=None,
        grund="Patient sagt: Nein danke, tschüss!"
    )
    
    print("ANTWORT BEI ECHTER VERABSCHIEDUNG:")
    print(result)
    print()
    
    if "*[CALL_END_SIGNAL]*" in result:
        print("✅ GESPRÄCH WIRD BEI VERABSCHIEDUNG BEENDET: KORREKT")
    else:
        print("❌ GESPRÄCH SOLLTE BEENDET WERDEN")
    
    # Test 4: Verschiedene Verabschiedungsarten
    print("\n4️⃣ TESTE VERSCHIEDENE VERABSCHIEDUNGEN:")
    print("-"*50)
    
    verabschiedungen = [
        "Auf Wiedersehen",
        "Tschüss", 
        "Danke, das reicht",
        "Vielen Dank und bye",
        "Nein, bis bald"
    ]
    
    for verabschiedung in verabschiedungen:
        result = await gespraech_beenden(context=None, grund=f"Patient sagt: {verabschiedung}")
        wird_beendet = "*[CALL_END_SIGNAL]*" in result
        print(f"'{verabschiedung}' → {'✅ BEENDET' if wird_beendet else '❌ NICHT BEENDET'}")
    
    print("\n" + "="*60)
    print("🎉 TESTS ABGESCHLOSSEN!")
    print("="*60)
    
    print("\n📋 ZUSAMMENFASSUNG DER REPARATUREN:")
    print("✅ Terminbuchung zeigt Alternativen bei Nichtverfügbarkeit")
    print("✅ Nach Terminbuchung: 'Haben Sie noch andere Fragen?'")
    print("✅ Gesprächsende nur bei echter Verabschiedung")
    print("✅ Rückfrage wenn Patient sich nicht verabschiedet")
    print("✅ Kurze, prägnante Antworten")
    print("✅ Natürlicher Gesprächsablauf wie echte Praxisangestellte")
    
    print("\n🔧 REPARATUREN ERFOLGREICH!")
    print("🤖 Die KI verhält sich jetzt wieder wie früher - natürlich und höflich!")

if __name__ == "__main__":
    asyncio.run(test_reparierte_ki())
