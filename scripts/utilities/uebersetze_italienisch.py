#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skript zur Massen-Übersetzung italienischer Begriffe auf Deutsch
"""

import re

def uebersetze_italienisch_zu_deutsch():
    """Übersetzt alle italienischen Begriffe in dental_tools.py auf Deutsch"""
    
    # Übersetzungstabelle
    uebersetzungen = {
        # Grundbegriffe
        "appuntamento": "Termin",
        "Appuntamento": "Termin", 
        "paziente": "Patient",
        "Paziente": "Patient",
        "disponibilità": "Verfügbarkeit",
        "Disponibilità": "Verfügbarkeit",
        
        # Fehlermeldungen
        "Mi dispiace": "Es tut mir leid",
        "Errore": "Fehler",
        "errore": "Fehler",
        "trovato": "gefunden",
        "non trovato": "nicht gefunden",
        "Non ho trovato": "Ich habe nicht gefunden",
        
        # Aktionen
        "riprogrammare": "umbuchen",
        "Riprogramma": "Bucht um",
        "cancellazione": "Stornierung",
        "Cancella": "Storniert",
        "registrata": "registriert",
        "felice": "gerne",
        "aiutarla": "Ihnen helfen",
        "verificare": "überprüfen",
        "verifica": "überprüft",
        "Verifica": "Überprüft",
        
        # Daten und Zeit
        "dati": "Daten",
        "orario": "Öffnungszeit",
        "prenotazione": "Buchung",
        "salva": "speichert",
        "Salva": "Speichert",
        
        # Spezifische Phrasen
        "costo indicativo": "Richtwert Kosten",
        "durata della seduta": "Behandlungsdauer",
        "si è verificato un errore": "ist ein Fehler aufgetreten",
        "La prego di riprovare": "Bitte versuchen Sie es erneut",
        "può specificare": "können Sie angeben",
        "Può verificare i dati": "Können Sie die Daten überprüfen",
        "La contatteremo": "Wir werden Sie kontaktieren",
        "il giorno prima": "am Tag vorher",
        "per confermare": "zur Bestätigung",
        
        # Längere Phrasen
        "Dettagli cancellazione": "Stornierungsdetails",
        "La cancellazione è stata registrata": "Die Stornierung wurde registriert",
        "Se desidera riprogrammare": "Falls Sie umbuchen möchten",
        "sarò felice di aiutarla": "helfe ich Ihnen gerne",
        "a trovare una nuova data": "einen neuen Termin zu finden",
        "Ho trovato appuntamenti per": "Ich habe Termine gefunden für",
        "Può specificare l'orario da cancellare": "Können Sie die zu stornierende Zeit angeben",
        "riprogrammato con successo": "erfolgreich umgebucht",
        "Vecchio appuntamento": "Alter Termin",
        "Nuovo appuntamento": "Neuer Termin",
        "il nuovo appuntamento": "den neuen Termin"
    }
    
    # Lese die Datei
    try:
        with open('src/dental_tools.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Führe Übersetzungen durch
        for italienisch, deutsch in uebersetzungen.items():
            if italienisch in content:
                count_before = content.count(italienisch)
                content = content.replace(italienisch, deutsch)
                count_after = content.count(italienisch)
                replaced = count_before - count_after
                if replaced > 0:
                    print(f"✅ '{italienisch}' → '{deutsch}' ({replaced}x ersetzt)")
        
        # Schreibe die Datei zurück
        if content != original_content:
            with open('src/dental_tools.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n🎯 Datei erfolgreich aktualisiert!")
            return True
        else:
            print("ℹ️ Keine Änderungen nötig - alle Begriffe bereits übersetzt")
            return True
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def teste_uebersetzung():
    """Testet ob noch italienische Begriffe vorhanden sind"""
    
    italienische_begriffe = [
        "appuntamento", "paziente", "disponibilità", 
        "Mi dispiace", "Errore", "trovato", "riprogrammare",
        "cancellazione", "registrata", "felice", "aiutarla", 
        "verificare", "dati", "orario", "prenotazione", "salva", "verifica"
    ]
    
    try:
        with open('src/dental_tools.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        gefundene = []
        for begriff in italienische_begriffe:
            if begriff in content:
                count = content.count(begriff)
                gefundene.append(f"{begriff} ({count}x)")
        
        if not gefundene:
            print("🏆 PERFEKT: Keine italienischen Begriffe mehr gefunden!")
            return True
        else:
            print("⚠️ Noch italienische Begriffe vorhanden:")
            for begriff in gefundene:
                print(f"   - {begriff}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("🚀 Massen-Übersetzung: Italienisch → Deutsch")
    print("=" * 50)
    
    print("\n📝 Schritt 1: Übersetzung durchführen...")
    erfolg_uebersetzung = uebersetze_italienisch_zu_deutsch()
    
    print("\n📝 Schritt 2: Ergebnis testen...")
    erfolg_test = teste_uebersetzung()
    
    print("\n" + "=" * 50)
    if erfolg_uebersetzung and erfolg_test:
        print("🏆 MASSEN-ÜBERSETZUNG ERFOLGREICH!")
        print("Alle italienischen Begriffe wurden auf Deutsch übersetzt!")
        print()
        print("🇩🇪 Die Zahnarztpraxis ist jetzt vollständig deutsch!")
    else:
        print("❌ Übersetzung unvollständig")
        print("Weitere manuelle Anpassungen erforderlich")
    
    return erfolg_uebersetzung and erfolg_test

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
