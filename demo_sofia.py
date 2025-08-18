#!/usr/bin/env python3
"""
Demo script for Sofia Dental Practice Assistant
Shows the main features for presentation
"""

import asyncio
import json
from datetime import datetime, timedelta
import httpx

class SofiaDentalDemo:
    def __init__(self):
        self.calendar_url = "http://localhost:3005"
        self.appointments = []
        
    async def check_calendar_connection(self):
        """Check if calendar server is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.calendar_url}/api/appointments")
                if response.status_code == 200:
                    print("[OK] Calendar server is running!")
                    appointments = response.json()
                    print(f"   Found {len(appointments)} appointments")
                    return True
        except Exception as e:
            print(f"[ERROR] Calendar server not accessible: {e}")
            print("   Please run: cd dental-calendar && npm start")
            return False
            
    async def create_demo_appointments(self):
        """Create sample appointments for demonstration"""
        print("\n[CALENDAR] Creating demo appointments...")
        
        demo_appointments = [
            {
                "patient_name": "Emma Johnson",
                "phone": "+44 7700 900001",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": "10:00",
                "end_time": "10:30",
                "treatment_type": "Check-up",
                "notes": "Regular 6-month check-up"
            },
            {
                "patient_name": "James Wilson",
                "phone": "+44 7700 900002",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": "11:00",
                "end_time": "11:45",
                "treatment_type": "Filling",
                "notes": "Upper molar filling"
            },
            {
                "patient_name": "Sarah Brown",
                "phone": "+44 7700 900003",
                "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "time": "14:00",
                "end_time": "15:00",
                "treatment_type": "Cleaning",
                "notes": "Professional dental cleaning"
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for appt in demo_appointments:
                try:
                    response = await client.post(
                        f"{self.calendar_url}/api/appointments",
                        json=appt
                    )
                    if response.status_code == 201:
                        print(f"   [OK] Created appointment for {appt['patient_name']}")
                    else:
                        print(f"   [FAIL] Failed to create appointment for {appt['patient_name']}")
                except Exception as e:
                    print(f"   [ERROR] {e}")
                    
    async def show_sofia_features(self):
        """Display Sofia's key features"""
        print("\n[SOFIA] AI ASSISTANT FEATURES:")
        print("=" * 50)
        
        features = [
            ("[VOICE] Recognition", "Natural English conversation"),
            ("[CALENDAR] Booking", "Smart scheduling with availability check"),
            ("[EMERGENCY] Handling", "Pain scale assessment (1-10)"),
            ("[TIME] Awareness", "CET timezone, practice hours aware"),
            ("[PATIENT] Management", "Name recognition and history"),
            ("[CALL] Management", "Automatic call ending on goodbye"),
            ("[PRACTICE] Info", "Dr. Smith's Dental Practice details"),
            ("[TREATMENT] Types", "Check-ups, cleanings, fillings, etc."),
        ]
        
        for feature, description in features:
            print(f"{feature:25} {description}")
            
    async def demo_conversation_flows(self):
        """Show example conversation flows"""
        print("\n[CHAT] EXAMPLE CONVERSATIONS:")
        print("=" * 50)
        
        conversations = [
            {
                "scenario": "Booking an appointment",
                "patient": "I need to book an appointment",
                "sofia": "I'll be happy to schedule an appointment for you. What do you need the appointment for?",
                "patient2": "I have a toothache",
                "sofia2": "I'm sorry to hear you're in pain. On a scale of 1 to 10, how severe is your pain?"
            },
            {
                "scenario": "Emergency handling",
                "patient": "I'm in severe pain, it's about an 8",
                "sofia": "I understand you're in significant pain. Let me find the earliest available appointment for you today.",
                "patient2": "Thank you",
                "sofia2": "What's your name please?"
            },
            {
                "scenario": "Polite ending",
                "patient": "That's all, thank you",
                "sofia": "Perfect! Thank you for calling Dr. Smith's Dental Practice. Have a great day and goodbye!",
                "patient2": "[Call automatically ends]",
                "sofia2": ""
            }
        ]
        
        for conv in conversations:
            print(f"\n[>] {conv['scenario']}:")
            print(f"   Patient: \"{conv['patient']}\"")
            print(f"   Sofia:   \"{conv['sofia']}\"")
            if conv['patient2']:
                print(f"   Patient: \"{conv['patient2']}\"")
            if conv['sofia2']:
                print(f"   Sofia:   \"{conv['sofia2']}\"")
                
    def show_presentation_tips(self):
        """Tips for the presentation"""
        print("\n[TIPS] PRESENTATION TIPS:")
        print("=" * 50)
        print("1. Start with calendar view - show existing appointments")
        print("2. Click 'New Appointment' to show manual booking")
        print("3. Demonstrate Sofia's greeting (time-aware)")
        print("4. Show emergency handling with pain scale")
        print("5. Book an appointment through conversation")
        print("6. Show automatic goodbye detection")
        print("7. Highlight real-time calendar updates")
        
        print("\n[KEY] POINTS TO EMPHASIZE:")
        print("- Fully in English (UK/US compatible)")
        print("- Professional medical terminology")
        print("- Time-zone aware (CET)")
        print("- Dr. Smith's Dental Practice branding")
        print("- Emergency prioritization system")
        print("- Automatic conversation management")

async def main():
    print("\n" + "="*60)
    print(" DR. SMITH'S DENTAL PRACTICE - SOFIA AI DEMO")
    print(" English Version - Presentation Helper")
    print("="*60)
    
    demo = SofiaDentalDemo()
    
    # Check calendar connection
    if await demo.check_calendar_connection():
        
        # Ask if user wants to create demo data
        create_demo = input("\nCreate demo appointments? (y/n): ")
        if create_demo.lower() == 'y':
            await demo.create_demo_appointments()
    
    # Show features
    await demo.show_sofia_features()
    
    # Show conversation examples  
    await demo.demo_conversation_flows()
    
    # Show presentation tips
    demo.show_presentation_tips()
    
    print("\n" + "="*60)
    print(" DEMO READY - Good luck with your presentation!")
    print("="*60)
    print()

if __name__ == "__main__":
    asyncio.run(main())