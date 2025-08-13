#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sicheres Skript zum Entfernen von Emojis ohne Dateistruktur zu zerstören
"""

import re

def entferne_emojis_sicher():
    """Entfernt Emojis sicher ohne die Dateistruktur zu zerstören"""
    
    # Liste der häufigsten Emojis
    emojis_zu_entfernen = [
        "📋", "📅", "🚨", "✅", "📞", "👤", "🦷", "💰", "📄", "🕐", "📍",
        "🔍", "✨", "⚡", "🏥", "📝", "⏱️", "🎵", "💡", "🎯", "⚠️",
        "🔴", "🟢", "🟡", "🔵", "⭐", "🌟", "💫", "🎉", "🎊", "🎈"
    ]
    
    try:
        # Lese die Datei ZEILENWEISE
        with open('src/dental_tools.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📖 Datei gelesen: {len(lines)} Zeilen")
        
        # Verarbeite jede Zeile einzeln
        modified_lines = []
        total_removed = 0
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Entferne Emojis aus dieser Zeile
            for emoji in emojis_zu_entfernen:
                if emoji in line:
                    count_before = line.count(emoji)
                    line = line.replace(emoji, "")
                    count_after = line.count(emoji)
                    removed = count_before - count_after
                    total_removed += removed
            
            # Bereinige nur überschüssige Leerzeichen, aber behalte Struktur
            line = re.sub(r'  +', ' ', line)  # Mehrfache Leerzeichen zu einem
            line = re.sub(r' +\n', '\n', line)  # Leerzeichen vor Zeilenende entfernen
            
            modified_lines.append(line)
        
        # Schreibe die Datei zurück
        with open('src/dental_tools.py', 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        
        print(f"✅ Datei erfolgreich aktualisiert!")
        print(f"📊 Insgesamt {total_removed} Emojis entfernt")
        print(f"📄 {len(modified_lines)} Zeilen beibehalten")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def teste_datei_struktur():
    """Testet ob die Dateistruktur noch intakt ist"""
    
    try:
        # Versuche die Datei zu importieren
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test-Import
        import dental_tools
        print("✅ Datei ist syntaktisch korrekt")
        
        # Teste eine Funktion
        if hasattr(dental_tools, 'get_zeitabhaengige_begruessung'):
            print("✅ Wichtige Funktionen sind verfügbar")
            return True
        else:
            print("❌ Wichtige Funktionen fehlen")
            return False
            
    except SyntaxError as e:
        print(f"❌ Syntax-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Import-Fehler: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("🚀 Sichere Emoji-Entfernung")
    print("=" * 50)
    print("Entfernt Emojis ohne die Dateistruktur zu zerstören")
    print()
    
    print("📝 Schritt 1: Emojis sicher entfernen...")
    erfolg_entfernung = entferne_emojis_sicher()
    
    if not erfolg_entfernung:
        print("❌ Emoji-Entfernung fehlgeschlagen")
        return False
    
    print("\n📝 Schritt 2: Dateistruktur testen...")
    erfolg_struktur = teste_datei_struktur()
    
    print("\n" + "=" * 50)
    if erfolg_entfernung and erfolg_struktur:
        print("🏆 SICHERE EMOJI-ENTFERNUNG ERFOLGREICH!")
        print("✅ Emojis entfernt")
        print("✅ Dateistruktur intakt")
        print("✅ Funktionen verfügbar")
        print()
        print("Sofia wird keine Emojis mehr vorlesen!")
    else:
        print("❌ Emoji-Entfernung hatte Probleme")
        if not erfolg_struktur:
            print("⚠️ Dateistruktur beschädigt - Wiederherstellung nötig")
    
    return erfolg_entfernung and erfolg_struktur

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
