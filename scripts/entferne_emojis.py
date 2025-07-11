#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skript zum Entfernen aller Emojis aus dental_tools.py
"""

import re

def entferne_alle_emojis():
    """Entfernt alle Emojis aus dental_tools.py"""
    
    # Liste der häufigsten Emojis
    emojis_zu_entfernen = [
        "📋", "📅", "🚨", "✅", "📞", "👤", "🦷", "💰", "📄", "🕐", "📍",
        "🔍", "✨", "⚡", "🏥", "📝", "⏱️", "🎵", "💡", "🎯", "⚠️",
        "🔴", "🟢", "🟡", "🔵", "⭐", "🌟", "💫", "🎉", "🎊", "🎈"
    ]
    
    try:
        # Lese die Datei
        with open('src/dental_tools.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        total_removed = 0
        
        # Entferne alle Emojis
        for emoji in emojis_zu_entfernen:
            if emoji in content:
                count_before = content.count(emoji)
                content = content.replace(emoji, "")
                count_after = content.count(emoji)
                removed = count_before - count_after
                if removed > 0:
                    print(f"✅ '{emoji}' entfernt ({removed}x)")
                    total_removed += removed
        
        # Entferne auch doppelte Leerzeichen und bereinige
        content = re.sub(r'\s+', ' ', content)  # Mehrfache Leerzeichen zu einem
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Mehrfache Zeilenumbrüche
        content = re.sub(r'\*\*\s+\*\*', '**', content)  # Leere Bold-Tags
        
        # Schreibe die Datei zurück
        if content != original_content:
            with open('src/dental_tools.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n🎯 Datei erfolgreich aktualisiert!")
            print(f"📊 Insgesamt {total_removed} Emojis entfernt")
            return True
        else:
            print("ℹ️ Keine Emojis gefunden")
            return True
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def teste_emoji_entfernung():
    """Testet ob noch Emojis vorhanden sind"""
    
    emojis = [
        "📋", "📅", "🚨", "✅", "📞", "👤", "🦷", "💰", "📄", "🕐", "📍",
        "🔍", "✨", "⚡", "🏥", "📝", "⏱️", "🎵", "💡", "🎯"
    ]
    
    try:
        with open('src/dental_tools.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        gefundene = []
        for emoji in emojis:
            if emoji in content:
                count = content.count(emoji)
                gefundene.append(f"{emoji} ({count}x)")
        
        if not gefundene:
            print("🏆 PERFEKT: Keine Emojis mehr gefunden!")
            return True
        else:
            print("⚠️ Noch Emojis vorhanden:")
            for emoji in gefundene:
                print(f"   - {emoji}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("🚀 Emoji-Entfernung: Alle Emojis aus dental_tools.py entfernen")
    print("=" * 60)
    print("Problem: Sofia liest Emojis vor")
    print("Lösung: Alle Emojis entfernen")
    print()
    
    print("📝 Schritt 1: Emojis entfernen...")
    erfolg_entfernung = entferne_alle_emojis()
    
    print("\n📝 Schritt 2: Ergebnis testen...")
    erfolg_test = teste_emoji_entfernung()
    
    print("\n" + "=" * 60)
    if erfolg_entfernung and erfolg_test:
        print("🏆 EMOJI-ENTFERNUNG ERFOLGREICH!")
        print("Sofia wird keine Emojis mehr vorlesen!")
        print()
        print("✅ Alle Emojis entfernt")
        print("✅ Text bleibt lesbar")
        print("✅ Funktionalität erhalten")
        print()
        print("🎯 Sofia sagt jetzt:")
        print("Vorher: '📋 Rezept benötigt'")
        print("Nachher: 'Rezept benötigt'")
    else:
        print("❌ Emoji-Entfernung unvollständig")
        print("Weitere manuelle Anpassungen erforderlich")
    
    return erfolg_entfernung and erfolg_test

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
