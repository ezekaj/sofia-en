"""
Sofia Integration für das Dental Calendar System
Verbindet Sofia Voice Assistant mit dem Kalender
"""
import httpx
import asyncio
from datetime import datetime, date, time
import logging

logger = logging.getLogger(__name__)

class DentalCalendarClient:
    """Client für das Dental Calendar System"""
    
    def __init__(self, calendar_url: str = "http://localhost:3005"):
        self.calendar_url = calendar_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def book_appointment(
        self,
        patient_name: str,
        patient_phone: str,
        requested_date: str,
        requested_time: str,
        treatment_type: str = None
    ) -> dict:
        """Bucht einen Termin über das Kalender-System"""
        try:
            response = await self.client.post(
                f"{self.calendar_url}/api/sofia/appointment",
                json={
                    "patientName": patient_name,
                    "patientPhone": patient_phone,
                    "requestedDate": requested_date,
                    "requestedTime": requested_time,
                    "treatmentType": treatment_type or "Beratung"
                }
            )
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Fehler beim Terminbuchen: {e}")
            return {
                "success": False,
                "message": "Verbindungsfehler zum Kalender-System. Bitte versuchen Sie es später erneut."
            }
    
    async def get_appointments(self) -> list:
        """Holt alle Termine aus dem Kalender"""
        try:
            response = await self.client.get(f"{self.calendar_url}/api/appointments")
            return response.json()
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Termine: {e}")
            return []
    
    async def check_availability(self, date: str, time: str) -> bool:
        """Prüft ob ein Zeitslot verfügbar ist"""
        appointments = await self.get_appointments()
        
        for appointment in appointments:
            apt_start = appointment.get('start', '')
            if apt_start.startswith(f"{date}T{time}"):
                return False
        
        return True
    
    async def close(self):
        """Schließt den Client"""
        await self.client.aclose()

# Tool-Funktionen für Sofia
calendar_client = DentalCalendarClient()

async def schedule_appointment_calendar(
    patient_name: str,
    patient_phone: str,
    appointment_date: str,
    appointment_time: str = None,
    treatment_type: str = None
) -> str:
    """
    Bucht einen Termin im Kalender-System
    """
    # Normalisiere Telefonnummer
    phone = patient_phone.replace(' ', '').replace('-', '')
    
    # Wenn keine Zeit angegeben, schlage Zeiten vor
    if not appointment_time:
        # Standard-Zeiten vorschlagen
        suggested_times = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
        
        for suggested_time in suggested_times:
            if await calendar_client.check_availability(appointment_date, suggested_time):
                appointment_time = suggested_time
                break
        
        if not appointment_time:
            return "Leider sind an diesem Tag keine Termine mehr frei. Bitte wählen Sie einen anderen Tag."
    
    result = await calendar_client.book_appointment(
        patient_name=patient_name,
        patient_phone=phone,
        requested_date=appointment_date,
        requested_time=appointment_time,
        treatment_type=treatment_type
    )
    
    if result.get("success"):
        return f"{result['message']} Der Termin erscheint sofort in unserem Kalender."
    else:
        return result.get("message", "Terminbuchung fehlgeschlagen")

async def check_appointments_calendar(patient_phone: str = None) -> str:
    """
    Zeigt alle Termine oder Termine eines Patienten
    """
    appointments = await calendar_client.get_appointments()
    
    if not appointments:
        return "Keine Termine gefunden."
    
    if patient_phone:
        # Filter nach Patient
        phone = patient_phone.replace(' ', '').replace('-', '')
        patient_appointments = [
            apt for apt in appointments 
            if apt.get('extendedProps', {}).get('phone', '').replace(' ', '').replace('-', '') == phone
        ]
        
        if not patient_appointments:
            return "Sie haben aktuell keine Termine bei uns."
        
        response = "Ihre Termine:\n"
        for apt in patient_appointments:
            start_date = apt['start'].split('T')[0]
            start_time = apt['start'].split('T')[1][:5]
            patient_name = apt.get('extendedProps', {}).get('patientName', 'Unbekannt')
            treatment = apt.get('extendedProps', {}).get('treatmentType', 'Allgemein')
            
            date_formatted = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d.%m.%Y')
            response += f"- {date_formatted} um {start_time} Uhr: {treatment}\n"
        
        return response.strip()
    else:
        # Alle heutigen Termine
        today = datetime.now().strftime('%Y-%m-%d')
        today_appointments = [
            apt for apt in appointments 
            if apt['start'].startswith(today)
        ]
        
        if not today_appointments:
            return "Heute sind keine Termine geplant."
        
        response = f"Termine heute ({datetime.now().strftime('%d.%m.%Y')}):\n"
        for apt in sorted(today_appointments, key=lambda x: x['start']):
            start_time = apt['start'].split('T')[1][:5]
            patient_name = apt.get('extendedProps', {}).get('patientName', 'Unbekannt')
            treatment = apt.get('extendedProps', {}).get('treatmentType', 'Allgemein')
            
            response += f"- {start_time} Uhr: {patient_name} ({treatment})\n"
        
        return response.strip()

async def get_available_times_calendar(appointment_date: str) -> str:
    """
    Zeigt verfügbare Zeiten für einen Tag
    """
    appointments = await calendar_client.get_appointments()
    
    # Standard Öffnungszeiten
    opening_hours = [
        "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"
    ]
    
    # Belegte Zeiten finden
    occupied_times = set()
    for apt in appointments:
        if apt['start'].startswith(appointment_date):
            time_part = apt['start'].split('T')[1][:5]
            occupied_times.add(time_part)
    
    # Verfügbare Zeiten
    available_times = [time for time in opening_hours if time not in occupied_times]
    
    if not available_times:
        return f"Am {appointment_date} sind leider keine Termine mehr frei."
    
    date_formatted = datetime.strptime(appointment_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    return f"Verfügbare Zeiten am {date_formatted}: {', '.join(available_times[:8])}"

# Test-Funktion
async def test_calendar_integration():
    """Testet die Kalender-Integration"""
    print("🧪 Teste Kalender-Integration...")
    
    # Test 1: Termin buchen
    result = await schedule_appointment_calendar(
        "Sofia Test Patient",
        "+49 30 11122334",
        "2024-07-25",
        "15:30",
        "Kontrolluntersuchung"
    )
    print(f"Terminbuchung: {result}")
    
    # Test 2: Termine abrufen
    appointments = await check_appointments_calendar()
    print(f"Heutige Termine: {appointments}")
    
    # Test 3: Verfügbarkeit prüfen
    available = await get_available_times_calendar("2024-07-25")
    print(f"Verfügbare Zeiten: {available}")
    
    await calendar_client.close()

if __name__ == "__main__":
    asyncio.run(test_calendar_integration())