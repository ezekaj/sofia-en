# Simple Patient Database for Dental Clinic
# In production, this should be replaced with a proper database system

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class PatientDatabase:
    def __init__(self, db_file: str = "patients.json"):
        self.db_file = db_file
        self.patients = self._load_database()
    
    def _load_database(self) -> Dict:
        """Load patient database from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_database(self) -> bool:
        """Save patient database to JSON file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.patients, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Datenbank: {e}")
            return False
    
    def add_patient(self, patient_data: Dict) -> str:
        """Add a new patient to the database"""
        phone = patient_data.get('phone', '')
        if not phone:
            return "Telefonnummer erforderlich"
        
        # Use phone as unique identifier
        patient_id = phone
        
        # Add timestamp
        patient_data['created_at'] = datetime.now().isoformat()
        patient_data['updated_at'] = datetime.now().isoformat()
        
        self.patients[patient_id] = patient_data
        
        if self._save_database():
            return f"Patient {patient_data.get('name', '')} erfolgreich hinzugefügt"
        else:
            return "Fehler beim Speichern der Daten"
    
    def get_patient(self, phone: str) -> Optional[Dict]:
        """Get patient information by phone number"""
        return self.patients.get(phone)
    
    def update_patient(self, phone: str, updated_data: Dict) -> str:
        """Update existing patient information"""
        if phone not in self.patients:
            return "Patient nicht gefunden"
        
        # Update fields
        for key, value in updated_data.items():
            if value:  # Only update non-empty values
                self.patients[phone][key] = value
        
        self.patients[phone]['updated_at'] = datetime.now().isoformat()
        
        if self._save_database():
            return "Patientendaten aktualisiert"
        else:
            return "Fehler beim Aktualisieren"
    
    def search_patients(self, search_term: str) -> List[Dict]:
        """Search patients by name or phone"""
        results = []
        search_term = search_term.lower()
        
        for patient_id, patient_data in self.patients.items():
            name = patient_data.get('name', '').lower()
            phone = patient_data.get('phone', '').lower()
            
            if search_term in name or search_term in phone:
                results.append(patient_data)
        
        return results
    
    def get_patient_appointments(self, phone: str) -> List[Dict]:
        """Get appointment history for a patient"""
        # This would integrate with the appointment system
        # For now, return empty list
        return []

class AppointmentDatabase:
    def __init__(self, db_file: str = "appointments.json"):
        self.db_file = db_file
        self.appointments = self._load_database()
    
    def _load_database(self) -> Dict:
        """Load appointments database from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_database(self) -> bool:
        """Save appointments database to JSON file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.appointments, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Errore nel salvataggio appuntamenti: {e}")
            return False
    
    def add_appointment(self, appointment_data: Dict) -> str:
        """Add a new appointment"""
        appointment_id = f"APP_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        appointment_data['id'] = appointment_id
        appointment_data['created_at'] = datetime.now().isoformat()
        appointment_data['status'] = 'confermato'
        
        self.appointments[appointment_id] = appointment_data
        
        if self._save_database():
            return appointment_id
        else:
            return ""
    
    def get_appointment(self, appointment_id: str) -> Optional[Dict]:
        """Get appointment by ID"""
        return self.appointments.get(appointment_id)
    
    def get_appointments_by_date(self, date: str) -> List[Dict]:
        """Get all appointments for a specific date"""
        appointments = []
        for app_id, app_data in self.appointments.items():
            if app_data.get('date') == date:
                appointments.append(app_data)
        return sorted(appointments, key=lambda x: x.get('time', ''))
    
    def get_appointments_by_patient(self, phone: str) -> List[Dict]:
        """Get all appointments for a specific patient"""
        appointments = []
        for app_id, app_data in self.appointments.items():
            if app_data.get('phone') == phone:
                appointments.append(app_data)
        return sorted(appointments, key=lambda x: x.get('date', ''))
    
    def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment"""
        if appointment_id in self.appointments:
            self.appointments[appointment_id]['status'] = 'cancellato'
            self.appointments[appointment_id]['cancelled_at'] = datetime.now().isoformat()
            return self._save_database()
        return False
    
    def update_appointment(self, appointment_id: str, updated_data: Dict) -> bool:
        """Update appointment information"""
        if appointment_id in self.appointments:
            for key, value in updated_data.items():
                if value:
                    self.appointments[appointment_id][key] = value
            self.appointments[appointment_id]['updated_at'] = datetime.now().isoformat()
            return self._save_database()
        return False
    
    def check_availability(self, date: str, time: str) -> bool:
        """Check if a time slot is available"""
        for app_id, app_data in self.appointments.items():
            if (app_data.get('date') == date and 
                app_data.get('time') == time and 
                app_data.get('status') == 'bestätigt'):
                return False
        return True
    
    def get_available_slots(self, date: str) -> List[str]:
        """Get available time slots for a date"""
        # Define working hours
        if date.endswith('6'):  # Saturday (assuming date format includes day of week)
            all_slots = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30"]
        else:
            all_slots = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", 
                        "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]
        
        # Remove booked slots
        booked_slots = []
        for app_id, app_data in self.appointments.items():
            if (app_data.get('date') == date and 
                app_data.get('status') == 'bestätigt'):
                booked_slots.append(app_data.get('time'))
        
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        return available_slots

# Global instances (in production, use proper dependency injection)
patient_db = PatientDatabase()
appointment_db = AppointmentDatabase()

# Helper functions for the tools
def save_patient_info(patient_data: Dict) -> str:
    """Save patient information to database"""
    return patient_db.add_patient(patient_data)

def get_patient_info(phone: str) -> Optional[Dict]:
    """Retrieve patient information"""
    return patient_db.get_patient(phone)

def save_appointment(appointment_data: Dict) -> str:
    """Save appointment to database"""
    return appointment_db.add_appointment(appointment_data)

def check_time_availability(date: str, time: str) -> bool:
    """Check if time slot is available"""
    return appointment_db.check_availability(date, time)

def get_available_times(date: str) -> List[str]:
    """Get available time slots for date"""
    return appointment_db.get_available_slots(date)
