#!/usr/bin/env python3
"""
Sofia Voice Demo - Direkte Integration mit Kalender
Simuliert Voice-Funktionalität für Testing
"""
import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
import requests

# Add path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'dental-calendar'))

try:
    from sofia_integration import (
        schedule_appointment_calendar,
        check_appointments_calendar,
        get_available_times_calendar
    )
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False

class SofiaVoiceDemo:
    def __init__(self):
        self.calendar_url = "http://localhost:3005"
        self.name = "Sofia"
        self.running = True
        
    async def start_demo(self):
        """Startet die Voice Demo"""
        print("🎤 Sofia Voice Demo startet...")
        print("=" * 60)
        
        # Test calendar connection
        if not await self.test_calendar_connection():
            print("❌ Kalender nicht erreichbar. Starten Sie: npm start im dental-calendar Ordner")
            return
            
        await self.show_welcome()
        await self.demo_voice_scenarios()
        
    async def test_calendar_connection(self):
        """Testet Kalender-Verbindung"""
        try:
            response = requests.get(f"{self.calendar_url}/api/appointments", timeout=5)
            if response.status_code == 200:
                print("✅ Kalender-System verbunden!")
                return True
        except Exception as e:
            print(f"❌ Kalender-Verbindung fehlgeschlagen: {e}")
        return False
        
    async def show_welcome(self):
        """Begrüßung"""
        current_time = datetime.now()
        if current_time.hour < 12:
            greeting = "Guten Morgen"
        elif current_time.hour < 18:
            greeting = "Guten Tag"
        else:
            greeting = "Guten Abend"
            
        print(f"\n🦷 {greeting}! Ich bin Sofia, Ihre digitale Zahnarzt-Assistentin.")
        print("🎤 Voice-Integration Demo - Simuliert Sprachinteraktion")
        print("\nIch kann Ihnen helfen bei:")
        print("• Termine buchen")
        print("• Verfügbare Zeiten anzeigen")
        print("• Ihre Termine anzeigen")
        print("• Praxisinformationen")
        
    async def demo_voice_scenarios(self):
        """Demonstriert verschiedene Voice-Szenarien"""
        scenarios = [
            {
                "name": "Terminbuchung per Voice",
                "description": "Patient möchte einen Termin buchen",
                "voice_input": "Hallo Sofia, ich möchte einen Termin buchen",
                "action": self.demo_appointment_booking
            },
            {
                "name": "Verfügbare Zeiten abfragen",
                "description": "Patient fragt nach freien Terminen",
                "voice_input": "Welche Zeiten sind morgen frei?",
                "action": self.demo_availability_check
            },
            {
                "name": "Meine Termine anzeigen",
                "description": "Patient möchte seine Termine sehen",
                "voice_input": "Zeige mir meine Termine",
                "action": self.demo_my_appointments
            },
            {
                "name": "Praxisinformationen",
                "description": "Patient fragt nach Öffnungszeiten",
                "voice_input": "Wie sind Ihre Öffnungszeiten?",
                "action": self.demo_practice_info
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*60}")
            print(f"🎬 Demo {i}: {scenario['name']}")
            print(f"📝 {scenario['description']}")
            print(f"🎤 Voice Input: \"{scenario['voice_input']}\"")
            print("="*60)
            
            input("Drücken Sie Enter um fortzufahren...")
            
            print(f"\n🤖 Sofia hört: \"{scenario['voice_input']}\"")
            print("🧠 Sofia verarbeitet...")
            await asyncio.sleep(1)  # Simulate processing
            
            await scenario['action']()
            
            print("\n✅ Voice-Interaktion abgeschlossen!")
            
        print(f"\n{'='*60}")
        print("🎉 Voice Demo abgeschlossen!")
        print("💡 In der echten Implementierung würde Sofia:")
        print("   • Sprache in Text umwandeln (Speech-to-Text)")
        print("   • Text mit KI verarbeiten")
        print("   • Antwort in Sprache umwandeln (Text-to-Speech)")
        print("   • Direkt mit dem Kalender interagieren")
        
    async def demo_appointment_booking(self):
        """Demo: Terminbuchung"""
        print("\n🤖 Sofia antwortet:")
        print("\"Gerne helfe ich Ihnen bei der Terminbuchung!\"")
        print("\"Wie ist Ihr Name?\"")
        
        # Simulate user response
        await asyncio.sleep(1)
        print("\n👤 Patient: \"Max Mustermann\"")
        
        print("\n🤖 Sofia: \"Ihre Telefonnummer bitte?\"")
        await asyncio.sleep(1)
        print("\n👤 Patient: \"030 12345678\"")
        
        print("\n🤖 Sofia: \"Welches Datum wünschen Sie?\"")
        await asyncio.sleep(1)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"\n👤 Patient: \"Morgen, also {tomorrow}\"")
        
        print("\n🤖 Sofia: \"Welche Uhrzeit passt Ihnen?\"")
        await asyncio.sleep(1)
        print("\n👤 Patient: \"14:30 Uhr\"")
        
        print("\n🧠 Sofia bucht den Termin...")
        
        try:
            if CALENDAR_AVAILABLE:
                result = await schedule_appointment_calendar(
                    "Max Mustermann",
                    "030 12345678", 
                    tomorrow,
                    "14:30",
                    "Beratung"
                )
                print(f"\n✅ Sofia: \"{result}\"")
                print("📅 Termin wurde im Kalender eingetragen!")
            else:
                print("\n✅ Sofia: \"Perfekt! Ihr Termin für morgen um 14:30 Uhr ist bestätigt.\"")
                print("📅 (Kalender-Integration simuliert)")
                
        except Exception as e:
            print(f"\n❌ Sofia: \"Entschuldigung, es gab ein Problem: {e}\"")
            
    async def demo_availability_check(self):
        """Demo: Verfügbarkeit prüfen"""
        print("\n🤖 Sofia antwortet:")
        print("\"Gerne zeige ich Ihnen die verfügbaren Zeiten!\"")
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"\"Für morgen, {tomorrow}:\"")
        
        try:
            if CALENDAR_AVAILABLE:
                result = await get_available_times_calendar(tomorrow)
                print(f"\n🤖 Sofia: \"{result}\"")
            else:
                print("\n🤖 Sofia: \"Verfügbare Zeiten morgen: 09:00, 10:30, 14:00, 15:30, 16:00\"")
                print("📅 (Kalender-Integration simuliert)")
                
        except Exception as e:
            print(f"\n❌ Sofia: \"Entschuldigung, ich kann die Zeiten gerade nicht abrufen: {e}\"")
            
    async def demo_my_appointments(self):
        """Demo: Meine Termine"""
        print("\n🤖 Sofia antwortet:")
        print("\"Gerne zeige ich Ihnen Ihre Termine!\"")
        print("\"Ihre Telefonnummer bitte?\"")
        
        await asyncio.sleep(1)
        print("\n👤 Patient: \"030 12345678\"")
        
        print("\n🧠 Sofia sucht Ihre Termine...")
        
        try:
            if CALENDAR_AVAILABLE:
                result = await check_appointments_calendar("030 12345678")
                print(f"\n🤖 Sofia: \"{result}\"")
            else:
                print("\n🤖 Sofia: \"Sie haben einen Termin am 28.07.2024 um 14:30 Uhr für eine Beratung.\"")
                print("📅 (Kalender-Integration simuliert)")
                
        except Exception as e:
            print(f"\n❌ Sofia: \"Entschuldigung, ich kann Ihre Termine gerade nicht abrufen: {e}\"")
            
    async def demo_practice_info(self):
        """Demo: Praxisinformationen"""
        print("\n🤖 Sofia antwortet:")
        print("\"Gerne informiere ich Sie über unsere Praxis!\"")
        print()
        print("🏥 Zahnarztpraxis Dr. Weber")
        print("📍 Hauptstraße 123, 10115 Berlin")
        print("📞 +49 30 12345678")
        print()
        print("🕒 Öffnungszeiten:")
        print("   Montag - Freitag: 8:00 - 18:00 Uhr")
        print("   Samstag: 9:00 - 13:00 Uhr")
        print("   Sonntag: Geschlossen")
        print()
        print("🚇 Anfahrt: U-Bahn Alexanderplatz, 5 Min. Fußweg")

async def main():
    """Hauptfunktion"""
    demo = SofiaVoiceDemo()
    await demo.start_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo beendet. Auf Wiedersehen!")
