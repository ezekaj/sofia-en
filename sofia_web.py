#!/usr/bin/env python3
"""
Sofia Web Interface - Deutsche Zahnarzt-Assistentin
Web-basierte Version mit Text-Interface und Kalender-Integration
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import asyncio
import os
import sys
from datetime import datetime

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
    print("⚠️ Kalender-Integration nicht verfügbar")

app = Flask(__name__)
CORS(app, origins=['http://localhost:3005', 'http://localhost:5001'])

class SofiaWebAgent:
    def __init__(self):
        self.name = "Sofia"
        
    async def process_message(self, message: str) -> str:
        """Verarbeitet Nachrichten von Benutzern"""
        message = message.lower().strip()
        
        # Begrüßung
        if any(word in message for word in ["hallo", "hi", "guten tag", "guten morgen"]):
            return self.get_greeting()
            
        # Termin buchen
        elif any(word in message for word in ["termin", "buchen", "vereinbaren"]):
            return "Gerne helfe ich Ihnen bei der Terminbuchung! Bitte verwenden Sie das Formular unten oder sagen Sie mir: Ihren Namen, Telefonnummer, gewünschtes Datum und Uhrzeit."
            
        # Verfügbare Zeiten
        elif any(word in message for word in ["verfügbar", "frei", "zeiten"]):
            return "Für welches Datum möchten Sie verfügbare Zeiten sehen? Bitte geben Sie das Datum im Format TT.MM.JJJJ an."
            
        # Praxisinfos
        elif any(word in message for word in ["öffnungszeiten", "adresse", "kontakt", "praxis"]):
            return self.get_practice_info()
            
        # Hilfe
        elif any(word in message for word in ["hilfe", "help", "was kannst du"]):
            return self.get_help()
            
        else:
            return "Entschuldigung, das habe ich nicht verstanden. Ich kann Ihnen bei Terminen, Praxisinformationen und allgemeinen Fragen helfen. Sagen Sie 'Hilfe' für mehr Optionen."
    
    def get_greeting(self) -> str:
        """Begrüßung basierend auf Tageszeit"""
        current_time = datetime.now()
        if current_time.hour < 12:
            greeting = "Guten Morgen"
        elif current_time.hour < 18:
            greeting = "Guten Tag"
        else:
            greeting = "Guten Abend"
            
        return f"{greeting}! Ich bin Sofia, Ihre digitale Zahnarzt-Assistentin. Wie kann ich Ihnen heute helfen?"
    
    def get_practice_info(self) -> str:
        """Praxisinformationen"""
        return """
🏥 **Zahnarztpraxis Dr. Weber**

📍 **Adresse:**
Hauptstraße 123
10115 Berlin

📞 **Telefon:** +49 30 12345678
📧 **E-Mail:** info@zahnarzt-weber.de

🕒 **Öffnungszeiten:**
• Montag - Freitag: 8:00 - 18:00 Uhr
• Samstag: 9:00 - 13:00 Uhr
• Sonntag: Geschlossen

🚇 **Anfahrt:**
U-Bahn: Alexanderplatz (5 Min. Fußweg)
Bus: Linie 100, 200 (Haltestelle Hauptstraße)
"""
    
    def get_help(self) -> str:
        """Hilfetext"""
        return """
🆘 **Ich kann Ihnen helfen bei:**

📅 **Terminen:**
• Termine buchen
• Verfügbare Zeiten anzeigen
• Ihre Termine anzeigen

🏥 **Praxisinformationen:**
• Öffnungszeiten
• Kontaktdaten
• Anfahrt

🦷 **Behandlungen:**
• Allgemeine Zahnheilkunde
• Prophylaxe
• Implantologie
• Ästhetische Zahnheilkunde

💡 **Beispiele:**
• "Ich möchte einen Termin buchen"
• "Welche Zeiten sind morgen frei?"
• "Wie sind Ihre Öffnungszeiten?"
"""

sofia = SofiaWebAgent()

@app.route('/')
def index():
    """Hauptseite"""
    return render_template('sofia.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat-Endpoint"""
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Keine Nachricht erhalten'}), 400
    
    try:
        # Process message asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(sofia.process_message(message))
        loop.close()
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Fehler: {str(e)}'}), 500

@app.route('/api/book_appointment', methods=['POST'])
def book_appointment():
    """Termin buchen"""
    if not CALENDAR_AVAILABLE:
        return jsonify({'error': 'Kalender-System nicht verfügbar'}), 503
    
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    date = data.get('date')
    time = data.get('time')
    treatment = data.get('treatment', 'Beratung')
    
    if not all([name, phone, date]):
        return jsonify({'error': 'Name, Telefon und Datum sind erforderlich'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            schedule_appointment_calendar(name, phone, date, time, treatment)
        )
        loop.close()
        
        return jsonify({
            'success': True,
            'message': result
        })
    except Exception as e:
        return jsonify({'error': f'Fehler beim Buchen: {str(e)}'}), 500

@app.route('/api/available_times/<date>')
def available_times(date):
    """Verfügbare Zeiten abrufen"""
    if not CALENDAR_AVAILABLE:
        return jsonify({'error': 'Kalender-System nicht verfügbar'}), 503
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_available_times_calendar(date))
        loop.close()
        
        return jsonify({
            'times': result
        })
    except Exception as e:
        return jsonify({'error': f'Fehler: {str(e)}'}), 500

@app.route('/api/livekit-token', methods=['POST'])
def get_livekit_token():
    """Generate LiveKit token for calendar integration"""
    try:
        data = request.json
        identity = data.get('identity', 'calendar-user')
        room = data.get('room', 'sofia-room')
        
        # For development, return a test token
        # In production, generate a proper token using LiveKit SDK
        import jwt
        import time
        
        token_data = {
            "exp": int(time.time()) + 86400,  # 24 hours
            "iss": "devkey",
            "sub": identity,
            "video": {
                "room": room,
                "roomJoin": True
            }
        }
        
        token = jwt.encode(token_data, "secret", algorithm="HS256")
        
        return jsonify({
            'token': token,
            'url': 'ws://localhost:7880'
        })
    except Exception as e:
        return jsonify({'error': f'Token generation failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("Sofia Web Interface startet...")
    print("Öffnen Sie: http://localhost:5001")
    print("Kalender-Integration:", "Verfügbar" if CALENDAR_AVAILABLE else "Nicht verfügbar")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
