#!/usr/bin/env python3
"""
Script zum Löschen aller Termine aus der Datenbank
"""
import sqlite3
import os

# Datenbank-Pfade
db_paths = [
    './dental-calendar/dental_calendar.db',
    './termine.db',
    './appointments.db'
]

def delete_all_appointments():
    """Löscht alle Termine aus allen gefundenen Datenbanken"""
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"\nBearbeite Datenbank: {db_path}")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Zähle aktuelle Termine
                cursor.execute("SELECT COUNT(*) FROM appointments")
                count = cursor.fetchone()[0]
                print(f"   Gefundene Termine: {count}")
                
                if count > 0:
                    # Lösche alle Termine
                    cursor.execute("DELETE FROM appointments")
                    conn.commit()
                    print(f"   Alle {count} Termine wurden geloescht!")
                else:
                    print("   Keine Termine zum Loeschen vorhanden.")
                
                # Prüfe ob erfolgreich gelöscht
                cursor.execute("SELECT COUNT(*) FROM appointments")
                new_count = cursor.fetchone()[0]
                print(f"   Termine nach Loeschung: {new_count}")
                
                conn.close()
                
            except Exception as e:
                print(f"   Fehler: {e}")
        else:
            print(f"\nDatenbank nicht gefunden: {db_path}")
    
    print("\nLoeschvorgang abgeschlossen!")

if __name__ == "__main__":
    print("Sofia Termin-Loeschung")
    print("=" * 40)
    
    # Bestätigung
    confirm = input("\nWARNUNG: Alle Termine werden geloescht! Fortfahren? (ja/nein): ")
    
    if confirm.lower() in ['ja', 'j', 'yes', 'y']:
        delete_all_appointments()
    else:
        print("Abgebrochen.")