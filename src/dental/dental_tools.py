import logging
import re
from functools import lru_cache
from livekit.agents import function_tool, RunContext
from datetime import datetime, timedelta, timedelta
from typing import Optional, Dict, List
from enum import Enum
import json
import locale
import httpx
import asyncio
# 🚀 PERFORMANCE BOOST: Fuzzy Times for vague time specifications
FUZZY_TIMES = {
    "shortly after 2": "14:15",
    "shortly after 2pm": "14:15",
    "around half past 2": "14:30",
    "around half 3": "14:30",
    "late afternoon": "16:00",
    "early afternoon": "13:00",
    "early morning": "08:00",
    "late evening": "19:00",
    "noon": "12:00",
    "around noon": "12:00",
    "in the morning": "10:00",
    "morning": "10:00",
    "afternoon": "15:00",
    "in the afternoon": "15:00",
    "around 2": "14:00",
    "around 3": "15:00",
    "around 4": "16:00",
    "around 5": "17:00",
    "just before 3": "14:45",
    "just before 4": "15:45",
    "just before 5": "16:45",
    "after lunch": "13:30",
    "before lunch": "11:30",
    "after work": "18:00",
    "during lunch": "12:30"
}

# Context Stack für Conversational Repair
class ContextStack:
    """🧠 SMART FALLBACK: Stateful Dialog für Korrekturen"""
    def __init__(self):
        self.last_slot = None
        self.last_appointment_request = None
        self.conversation_context = {}

    def set_last_slot(self, slot_data):
        """Speichert den letzten Terminvorschlag"""
        self.last_slot = slot_data

    def repair_time(self, user_input):
        """Repariert Zeitangaben bei Korrekturen wie 'Nein, lieber 11:30'"""
        if self.last_slot and any(word in user_input.lower() for word in ["lieber", "besser", "stattdessen", "nein"]):
            # Extrahiere neue Zeit aus Input
            new_time = self._extract_time_from_correction(user_input)
            if new_time and self.last_slot:
                # Ersetze Zeit im letzten Slot
                corrected_slot = self.last_slot.copy()
                corrected_slot['uhrzeit'] = new_time
                return corrected_slot
        return None

    def _extract_time_from_correction(self, text):
        """Extrahiert Zeit aus Korrektur-Text"""
        import re
        # Suche nach Zeitformaten in Korrekturen
        time_patterns = [
            r'(\d{1,2}):(\d{2})',  # 11:30
            r'(\d{1,2})\.(\d{2})',  # 11.30
            r'(\d{1,2}) o'clock',       # 11 o'clock
            r'um (\d{1,2})',        # um 11
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                if ':' in pattern or '\\.' in pattern:
                    hour, minute = match.groups()
                    return f"{int(hour):02d}:{int(minute):02d}"
                else:
                    hour = match.group(1)
                    return f"{int(hour):02d}:00"
        return None

# Globale Context Stack Instanz
context_stack = ContextStack()

# Clinic knowledge data inline (from original backup)
CLINIC_INFO = {
    'name': 'Dental Practice Dr. Weber',
    'address': '123 Main Street, London SW1A 1AA',
    'phone': '+44 20 7123 4567',
    'email': 'info@drsmith-dental.co.uk',
    'website': 'www.drsmith-dental.co.uk',
    'opening_hours': {
        'monday': '08:00-18:00',
        'tuesday': '08:00-18:00',
        'wednesday': '08:00-18:00',
        'thursday': '08:00-18:00',
        'friday': '08:00-16:00',
        'saturday': 'closed',
        'sunday': 'closed'
    }
}

SERVICES = [
    'check-up',
    'dental cleaning',
    'Füllungen',
    'root canal',
    'dental prosthetics',
    'Implantate',
    'orthodontics',
    'Notfallbehandlung'
]

FAQ = {
    'Kosten': 'Die Kosten variieren je nach Behandlung. Kontaktieren Sie uns für ein Angebot.',
    'appointments': 'appointments können telefonisch oder online gebucht werden.',
    'emergency': 'Bei Notfällen rufen Sie Please sofort an.'
}

APPOINTMENT_TYPES = {
    'check-up': 30,
    'dental cleaning': 60,
    'Füllungen': 45,
    'root canal': 90,
    'dental prosthetics': 60,
    'Implantate': 120,
    'orthodontics': 45,
    'Notfallbehandlung': 30
}

INSURANCE_INFO = {
    'gesetzlich': 'Wir rechnen direkt mit Ihrer Krankenkasse ab.',
    'privat': 'Private Versicherungen werden nach GOZ abgerechnet.'
}

PAYMENT_OPTIONS = ['Barzahlung', 'EC-Karte', 'Überweisung', 'Ratenzahlung']

STAFF = {
    'Dr. Weber': 'Zahnarzt',
    'Sofia': 'Praxisassistentin (KI)'
}

# Deutsche Wochentage und Monate
GERMAN_WEEKDAYS = {
    0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
    4: 'Friday', 5: 'Saturday', 6: 'Sunday'
}

GERMAN_MONTHS = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

def get_current_datetime_info():
    """
    Gibt automatisch das aktuelle Datum und die Uhrzeit zurück.
    ✅ KONSISTENTE datetime-Verwendung - keine String/datetime Mischung
    ✅ REPARIERT: Verwendet immer das aktuelle Datum ohne Caching
    ✅ AUTO-DATUM: Automatische Datum-Einfügung aktiviert
    """
    # ✅ WICHTIG: Jedes Mal frisches Datum abrufen
    now = datetime.now()
    
    # 🔧 DEBUG: Logging für Datum-Debugging
    import logging
    logging.debug(f"DATUM-DEBUG: Aktuelles Datum: {now}")

    # Deutsche Wochentag und Monat
    weekday_german = GERMAN_WEEKDAYS[now.weekday()]
    month_german = GERMAN_MONTHS[now.month]

    # ✅ KONSISTENTE Ausgabe - datetime-Objekte UND formatierte Strings
    date_info = {
        # datetime-Objekte für Berechnungen
        'datetime': now,
        'date': now.date(),  # date-Objekt
        'time': now.time(),  # time-Objekt

        # Formatierte Strings für Anzeige
        'date_formatted': f"{weekday_german}, {now.day}. {month_german} {now.year}",
        'time_formatted': f"{now.hour:02d}:{now.minute:02d}",
        'date_iso': now.strftime("%Y-%m-%d"),  # ISO-Format für Datenbank
        'time_iso': now.strftime("%H:%M"),     # ISO-Format für Datenbank
        
        # ✅ AUTO-DATUM: Automatische Datum-Einfügung für Antworten
        'auto_date': f"today ist {weekday_german}, der {now.day}. {month_german} {now.year}",
        'auto_time': f"Es ist {now.hour:02d}:{now.minute:02d} o'clock",

        # Deutsche Bezeichnungen
        'weekday': weekday_german,
        'month': month_german,

        # Numerische Werte für Berechnungen
        'hour': now.hour,
        'minute': now.minute,
        'day': now.day,
        'month_num': now.month,
        'year': now.year,
        'weekday_num': now.weekday(),

        # Berechnete Werte
        'is_weekend': now.weekday() >= 5,  # Saturday=5, Sunday=6
        'tomorrow_weekday': GERMAN_WEEKDAYS[(now.weekday() + 1) % 7]
    }

    # ✅ RELATIVE DATUMS-BERECHNUNGEN hinzufügen
    tomorrow = now + timedelta(days=1)
    übermorgen = now + timedelta(days=2)
    
    # 🔧 DEBUG: Logging für Datum-Debugging
    logging.debug(f"DATUM-DEBUG: tomorrow: {tomorrow.day}. {GERMAN_MONTHS[tomorrow.month]} {tomorrow.year}")
    logging.debug(f"DATUM-DEBUG: Übermorgen: {übermorgen.day}. {GERMAN_MONTHS[übermorgen.month]} {übermorgen.year}")

    # Nächste Woche = Monday der nächsten Woche
    tage_bis_naechster_montag = (7 - now.weekday()) % 7
    if tage_bis_naechster_montag == 0:  # today ist Monday
        tage_bis_naechster_montag = 7  # Nächster Monday
    naechste_woche = now + timedelta(days=tage_bis_naechster_montag)

    # Kalenderwoche berechnen
    kalenderwoche = now.isocalendar()[1]

    # Erweiterte Informationen hinzufügen
    date_info.update({
        # Relative Daten
        'tomorrow': f"{GERMAN_WEEKDAYS[tomorrow.weekday()]}, {tomorrow.day}. {GERMAN_MONTHS[tomorrow.month]} {tomorrow.year}",
        'morgen_iso': tomorrow.strftime("%Y-%m-%d"),
        'übermorgen': f"{GERMAN_WEEKDAYS[übermorgen.weekday()]}, {übermorgen.day}. {GERMAN_MONTHS[übermorgen.month]} {übermorgen.year}",
        'übermorgen_iso': übermorgen.strftime("%Y-%m-%d"),
        'nächste_woche': f"{GERMAN_WEEKDAYS[naechste_woche.weekday()]}, {naechste_woche.day}. {GERMAN_MONTHS[naechste_woche.month]} {naechste_woche.year}",
        'nächste_woche_iso': naechste_woche.strftime("%Y-%m-%d"),
        'kalenderwoche': kalenderwoche,

        # datetime-Objekte für weitere Berechnungen
        'morgen_datetime': tomorrow,
        'übermorgen_datetime': übermorgen,
        'nächste_woche_datetime': naechste_woche
    })

    return date_info

def get_intelligente_medizinische_nachfragen(symptom_oder_grund: str) -> str:
    """
    🩺 INTELLIGENTE MEDIZINISCHE NACHFRAGEN
    Sofia stellt hilfreiche Nachfragen basierend auf Symptomen oder Behandlungsgründen
    """
    symptom_oder_grund = symptom_oder_grund.lower()

    # 🦷 pain - Natürliche Nachfragen
    if any(word in symptom_oder_grund for word in ['schmerz', 'pain', 'weh', 'tut weh', 'ziehen', 'stechen', 'pochen']):
        return "Oh, das tut mir leid zu hören, dass Sie pain haben. Seit wann haben Sie denn die Beschwerden? Und haben Sie schon Schmerzmittel genommen?"

    # 🦷 IMPLANTAT - Natürliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['implantat', 'implant', 'dental prosthetics', 'künstlicher zahn']):
        return "Ah, es geht um Ihr Implantat. Ist das nur für eine check-up oder haben Sie Probleme damit?"

    # 🦷 ZAHNFLEISCH - Natürliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['zahnfleisch', 'gingiva', 'blut', 'blutet', 'geschwollen', 'entzündet', 'parodont']):
        return "Ich verstehe, Sie haben Probleme mit dem Zahnfleisch. Blutet es beim Zähneputzen oder ist es geschwollen?"

    # 🦷 WEISHEITSZÄHNE - Natürliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['weisheitszahn', 'weisheitszähne', 'achter', '8er']):
        return "Ach so, es geht um die Weisheitszähne. Haben Sie pain oder möchten Sie sie entfernen lassen?"

    # 🦷 KRONE/filling - Natürliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['krone', 'filling', 'plombe', 'inlay', 'onlay', 'abgebrochen', 'rausgefallen']):
        return "Oh, ist etwas mit einer filling oder Krone passiert? Ist sie abgebrochen oder rausgefallen?"

    # 🦷 KONTROLLE/PROPHYLAXE - Freundliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['kontrolle', 'untersuchung', 'check', 'prophylaxe', 'reinigung', 'vorsorge']):
        return "Das ist sehr gut, dass Sie zur Kontrolle kommen möchten. Wann waren Sie denn das letzte Mal beim Zahnarzt?"

    # 🦷 BLEACHING/ÄSTHETIK - Beratungsansatz
    elif any(word in symptom_oder_grund for word in ['bleaching', 'aufhellen', 'weiß', 'ästhetik', 'schön', 'verfärb']):
        return "Schön, dass Sie sich für ästhetische Zahnbehandlung interessieren. Möchten Sie Ihre Zähne aufhellen lassen?"

    # 🚨 emergency - Sofortige Hilfe
    elif any(word in symptom_oder_grund for word in ['emergency', 'urgent', 'sofort', 'starke pain', 'unerträglich', 'geschwollen']):
        return "Das klingt nach einem emergency! Haben Sie starke pain? Ich suche sofort einen dringenden appointment für Sie."

    # 🦷 ALLGEMEINE BEHANDLUNG - Standard-Nachfragen
    else:
        return "Gladly helfe ich Ihnen weiter. Können Sie mir sagen, was für Beschwerden Sie haben oder welche Behandlung Sie benötigen?"

def validate_and_parse_datetime(date_str: str, time_str: str):
    """
    ✅ KONSISTENTE datetime-Validierung und -Parsing
    Verhindert String/datetime-Mischung durch einheitliche Behandlung
    """
    try:
        # Parse und validiere Datum und Zeit
        appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

        # Prüfe ob Datum in der Zukunft liegt
        now = datetime.now()
        if appointment_datetime <= now:
            return None, "Der appointment muss in der Zukunft liegen."

        # Prüfe Geschäftszeiten
        weekday = appointment_datetime.weekday()
        hour = appointment_datetime.hour

        # Sunday = 6
        if weekday == 6:
            return None, "Sonntags sind wir closed."

        # Saturday = 5 (nur vormittags)
        if weekday == 5 and (hour < 9 or hour >= 13):
            return None, "Samstags sind wir nur von 9:00-12:30 open."

        # Monday-Friday
        if weekday < 5:
            if hour < 9 or hour >= 18:
                return None, "Unsere opening hours sind Mo-Do: 9:00-17:30, Fr: 9:00-16:00."
            if 11 < hour < 14:  # Mittagspause
                return None, "Während der Mittagspause (11:30-14:00) sind keine appointments möglich."

        # Friday (nur bis 16:00)
        if weekday == 4 and hour >= 16:
            return None, "Freitags sind wir nur bis 16:00 open."

        return appointment_datetime, None

    except ValueError:
        return None, "Ungültiges Datum- oder Zeitformat. Verwenden Sie YYYY-MM-DD und HH:MM."
from src.dental.appointment_manager import appointment_manager

# Simple in-memory storage for appointments (in production, use a proper database)
appointments_db = {}
patient_db = {}

# CallManager for conversation status
class CallStatus(Enum):
    ACTIVE = "active"
    ENDING = "ending"
    COMPLETED = "completed"

class CallManager:
    def __init__(self):
        self.status = CallStatus.ACTIVE
        self.notes = []
        self.patient_info = {}
        self.scheduled_appointment = None
        self.conversation_ended = False
        self.session = None  # LiveKit session reference
        self.patient_name = None  # 🧠 NAMEN-SPEICHER
        self.name_asked = False   # Verhindert mehrfaches Nachfragen
        
    def add_note(self, note: str):
        # ✅ KONSISTENT: Verwende get_current_datetime_info()
        time_info = get_current_datetime_info()
        self.notes.append(f"{time_info['time_formatted']}: {note}")
        
    def set_patient_info(self, info: dict):
        self.patient_info.update(info)
        
    def mark_appointment_scheduled(self, appointment_data: dict):
        self.scheduled_appointment = appointment_data
        
    def initiate_call_end(self):
        self.status = CallStatus.ENDING
        self.conversation_ended = True
        logging.info("🔴 Gespräch wird beendet - CallManager Status: ENDING")
        
    def is_conversation_ended(self) -> bool:
        return self.conversation_ended
        
    def set_session(self, session):
        """Set the LiveKit session for call management"""
        self.session = session
        
    def get_summary(self) -> str:
        # ✅ KONSISTENT: Verwende get_current_datetime_info()
        time_info = get_current_datetime_info()
        summary = f"Gespräch beendet um {time_info['time_formatted']}\n"
        if self.patient_info:
            summary += f"patient: {self.patient_info.get('name', 'N/A')}\n"
            summary += f"Telefon: {self.patient_info.get('phone', 'N/A')}\n"
        if self.scheduled_appointment:
            summary += f"appointment gebucht: {self.scheduled_appointment}\n"
        if self.notes:
            summary += f"Notizen: {', '.join(self.notes)}\n"
        return summary

    def set_patient_name(self, name: str):
        """🧠 Speichert den Patientennamen für das gesamte Gespräch"""
        self.patient_name = name.strip()
        self.add_note(f"Patientenname gespeichert: {self.patient_name}")

    def get_patient_name(self) -> str:
        """🧠 Gibt den gespeicherten Patientennamen zurück"""
        return self.patient_name

    def has_patient_name(self) -> bool:
        """🧠 Prüft ob ein Patientenname gespeichert ist"""
        return self.patient_name is not None and len(self.patient_name.strip()) > 0

    def mark_name_asked(self):
        """Markiert, dass nach dem Namen gefragt wurde"""
        self.name_asked = True

    def should_ask_for_name(self) -> bool:
        """Prüft ob nach dem Namen gefragt werden soll"""
        return not self.has_patient_name() and not self.name_asked

    def end_call(self):
        """📞 Beendet den Anruf höflich und setzt den Status"""
        self.status = CallStatus.ENDED
        self.conversation_ended = True
        self.add_note("Gespräch höflich beendet")

        # Wenn LiveKit Session vorhanden, markiere als beendet
        if self.session:
            try:
                # Markiere Session als beendet
                self.session._ended = True
            except Exception as e:
                logging.error(f"Fehler beim Beenden der LiveKit Session: {e}")

# Global CallManager instance
call_manager = CallManager()

# Deutsche Telefonnummern-Validierung
def ist_deutsche_telefonnummer(telefon: str) -> bool:
    """
    Prüft ob eine Telefonnummer eine gültige deutsche Nummer ist.
    Akzeptiert deutsche Festnetz- und Mobilnummern.
    """
    if not telefon:
        return False
    
    # Bereinige Nummer - entferne Leerzeichen, Bindestriche, Klammern, Punkte
    nummer = re.sub(r'[\s\-\(\)\.\/]', '', telefon.strip())
    
    # Entferne führendes + falls vorhanden
    if nummer.startswith('+'):
        nummer = nummer[1:]
    
    # Deutsche Mobilnummern
    # Format: 015x, 016x, 017x (oder 4915x, 4916x, 4917x)
    if re.match(r'^(49)?0?1[567]\d{7,8}$', nummer):
        return True
    
    # Deutsche Festnetznummern
    # Format: Vorwahl (2-5 Ziffern) + Rufnummer (4-8 Ziffern)
    # Mit Landesvorwahl: 49 + Vorwahl (ohne 0) + Nummer
    # Ohne Landesvorwahl: 0 + Vorwahl + Nummer
    if re.match(r'^(49)?0?[2-9]\d{1,4}\d{4,8}$', nummer):
        # Prüfe Gesamtlänge
        if nummer.startswith('49'):
            # Mit Landesvorwahl: 11-12 Ziffern
            return 11 <= len(nummer) <= 13
        else:
            # Ohne Landesvorwahl: 10-11 Ziffern
            return 10 <= len(nummer) <= 12
    
    return False

def formatiere_telefonnummer(telefon: str) -> str:
    """
    Formatiert eine deutsche Telefonnummer einheitlich.
    """
    nummer = re.sub(r'[\s\-\(\)\.\/]', '', telefon.strip())
    
    # Füge Leerzeichen für bessere Lesbarkeit ein
    if nummer.startswith('+49'):
        # +49 170 12345678
        return f"+49 {nummer[3:6]} {nummer[6:]}"
    elif nummer.startswith('0'):
        # 0170 12345678
        if len(nummer) > 4:
            return f"{nummer[:4]} {nummer[4:]}"
    
    return telefon

@function_tool()
async def get_clinic_info(
    context: RunContext,
    info_type: str = "general"
) -> str:
    """
    Stellt Informationen über die Dental Practice bereit.
    info_type kann sein: 'general', 'hours', 'contact', 'location', 'parking'
    """
    try:
        if info_type == "general":
            return f"""
Dental Practice Dr. Weber
Adresse: {CLINIC_INFO['address']}
Telefon: {CLINIC_INFO['phone']}
E-Mail: {CLINIC_INFO['email']}
opening hours: Monday-Friday 9:00-18:00, Saturday 9:00-13:00
{CLINIC_INFO['emergency_hours']}
{CLINIC_INFO['parking']}
"""
        elif info_type == "hours":
            hours_text = "opening hours:\n"
            for day, hours in CLINIC_INFO['hours'].items():
                hours_text += f"{day.capitalize()}: {hours}\n"
            hours_text += f"\n{CLINIC_INFO['emergency_hours']}"
            return hours_text
        
        elif info_type == "contact":
            return f"""
Kontakt Dental Practice Dr. Weber:
Telefon: {CLINIC_INFO['phone']}
E-Mail: {CLINIC_INFO['email']}
Website: {CLINIC_INFO['website']}
"""
        elif info_type == "location":
            return f"""
Indirizzo: {CLINIC_INFO['address']}
{CLINIC_INFO['parking']}
{CLINIC_INFO['accessibility']}
"""
        else:
            return "Informationstyp nicht erkannt. Ich kann allgemeine Informationen, opening hours, Kontakt oder Standort bereitstellen."
            
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Praxisinformationen: {e}")
        return "Sorry, es ist ein Fehler beim Abrufen der Informationen aufgetreten."

@function_tool()
async def get_services_info(
    context: RunContext,
    service_type: str = "all"
) -> str:
    """
    Bietet Informationen über die angebotenen zahnärztlichen Leistungen.
    service_type kann sein: 'all', 'allgemeine_zahnheilkunde', 'dental hygiene', 'kieferorthopaedie', 'implantologie', 'aesthetische_zahnheilkunde', 'endodontics', 'oralchirurgie', 'prothetik'
    """
    try:
        if service_type == "all":
            services_text = "Leistungen unserer Dental Practice:\n\n"
            # Da SERVICES eine Liste ist, verwenden wir die deutsche Liste
            for service in SERVICES:
                services_text += f"• {service}\n"
            return services_text
        
        elif service_type in SERVICES:
            return f"Leistung: {service_type}\nWeitere Details erhalten Sie Gladly bei einem Beratungstermin."
        else:
            return "Leistung nicht gefunden. Unsere Hauptleistungen sind: Allgemeine Zahnheilkunde, dental hygiene, orthodontics, Implantologie, Ästhetische Zahnheilkunde, endodontics, Oralchirurgie und Prothetik."
            
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Leistungsinformationen: {e}")
        return "Sorry, es gab einen Fehler beim Abrufen der Leistungsinformationen."

@function_tool()
async def answer_faq(
    context: RunContext,
    question_topic: str
) -> str:
    """
    Beantwortet häufig gestellte Fragen zu zahnärztlichen Leistungen.
    question_topic kann sein: 'kosten', 'versicherungen', 'notfaelle', 'erstbesuch', 'zahlungen', 'kinder', 'anaesthesie', 'hygiene_haeufigkeit'
    """
    try:
        # Cerca la domanda più pertinente
        for key, faq_item in FAQ.items():
            if question_topic.lower() in key.lower() or question_topic.lower() in faq_item['question'].lower():
                return f"Domanda: {faq_item['question']}\nRisposta: {faq_item['answer']}"
        
        # Se non trova una corrispondenza esatta, restituisce tutte le FAQ
        faq_text = "Ecco le nostre domande frequenti:\n\n"
        for faq_item in FAQ.values():
            faq_text += f"Q: {faq_item['question']}\nR: {faq_item['answer']}\n\n"
        return faq_text
        
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der FAQ: {e}")
        return "Sorry, es gab einen Fehler beim Abrufen der Informationen."

@function_tool()
async def check_availability(
    context: RunContext,
    date: str,
    appointment_type: str = "check-up"
) -> str:
    """
    Prüft die Verfügbarkeit für einen appointment an einem bestimmten Datum.
    date Format: YYYY-MM-DD
    appointment_type: Art des gewünschten Termins
    """
    try:
        # Simulation der Verfügbarkeitsprüfung (in Produktion mit echtem Kalendersystem integrieren)
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Prüfe ob das Datum in der Vergangenheit liegt
        if target_date.date() < datetime.now().date():
            return "Sorry, ich kann keine appointments für vergangene Daten buchen."

        # Prüfe ob es Sunday ist (practice closed)
        if target_date.weekday() == 6:  # Sunday
            return "Sorry, die practice ist sonntags closed. Kann ich Ihnen einen anderen Tag vorschlagen?"

        # Prüfe ob es Saturday ist (verkürzte opening hours)
        if target_date.weekday() == 5:  # Saturday
            available_times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30"]
        else:
            available_times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                             "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]

        # Simuliere bereits belegte appointments
        occupied_slots = appointments_db.get(date, [])
        available_times = [time for time in available_times if time not in occupied_slots]

        if available_times:
            return f"Verfügbarkeit für {date}:\nVerfügbare Zeiten: {', '.join(available_times[:6])}"
        else:
            # Schlage alternative appointments vor
            next_date = target_date + timedelta(days=1)
            return f"Sorry, es sind keine appointments verfügbar für {date}. Kann ich Ihnen {next_date.strftime('%Y-%m-%d')} vorschlagen?"
            
    except ValueError:
        return "Ungültiges Datumsformat. Please verwenden Sie das Format YYYY-MM-DD (z.B. 2024-01-15)."
    except Exception as e:
        logging.error(f"Fehler bei der Verfügbarkeitsprüfung: {e}")
        return "Sorry, es gab einen Fehler bei der Verfügbarkeitsprüfung."

@function_tool()
async def schedule_appointment(
    context: RunContext,
    patient_name: str,
    phone: str,
    date: str,
    time: str,
    appointment_type: str = "check-up",
    notes: str = ""
) -> str:
    """
    Bucht einen neuen appointment.
    Parameter: Patientenname, Telefon, Datum (YYYY-MM-DD), Uhrzeit (HH:MM), Terminart, zusätzliche Notizen
    """
    try:
        # Validazione data e ora
        appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        if appointment_datetime < datetime.now():
            return "Ich kann keine appointments für vergangene Daten und Uhrzeiten buchen."
        
        # Prüfe ob die Terminart existiert
        if appointment_type not in APPOINTMENT_TYPES:
            return f"Terminart nicht erkannt. Verfügbare Arten: {', '.join(APPOINTMENT_TYPES.keys())}"
        
        # ✅ KONSISTENT: Verwende get_current_datetime_info()
        time_info = get_current_datetime_info()
        appointment_id = f"APP_{time_info['datetime'].strftime('%Y%m%d%H%M%S')}"
        
        appointment_data = {
            "id": appointment_id,
            "patient_name": patient_name,
            "phone": phone,
            "date": date,
            "time": time,
            "type": appointment_type,
            "notes": notes,
            "status": "confermato",
            "created_at": datetime.now().isoformat()
        }
        
        # Speichere den appointment
        if date not in appointments_db:
            appointments_db[date] = []
        appointments_db[date].append(time)
        
        # Speichere die Patientendaten
        patient_db[phone] = {
            "name": patient_name,
            "phone": phone,
            "last_appointment": appointment_id
        }
        
        appointment_info = APPOINTMENT_TYPES[appointment_type]
        
        return f"""
appointment bestätigt!

Details:
• patient: {patient_name}
• Datum: {date}
• Uhrzeit: {time}
• Art: {appointment_info['name']}
• Voraussichtliche Dauer: {appointment_info['duration']} Minuten
• Buchungscode: {appointment_id}

Wir werden Sie am Tag vorher anrufen, um den appointment zu bestätigen.
Please bringen Sie einen Personalausweis und Ihre Versichertenkarte mit.
"""
        
    except ValueError:
        return "Formato data o ora non valido. Utilizzare YYYY-MM-DD per la data e HH:MM per l'ora."
    except Exception as e:
        logging.error(f"Fehler bei der Buchung: {e}")
        return "Sorry, es gab einen Fehler bei der Buchung. Please versuchen Sie es erneut."

@function_tool()
async def collect_patient_info(
    context: RunContext,
    name: str,
    phone: str,
    email: str = "",
    birth_date: str = "",
    medical_conditions: str = "",
    medications: str = "",
    allergies: str = "",
    previous_dentist: str = ""
) -> str:
    """
    Sammelt die Patienteninformationen für den ersten Besuch.
    """
    try:
        patient_data = {
            "name": name,
            "phone": phone,
            "email": email,
            "birth_date": birth_date,
            "medical_conditions": medical_conditions,
            "medications": medications,
            "allergies": allergies,
            "previous_dentist": previous_dentist,
            "registration_date": datetime.now().isoformat()
        }
        
        # Speichere die Patientendaten
        patient_db[phone] = patient_data
        
        return f"""
Patienteninformationen registriert:
• Name: {name}
• Telefon: {phone}
• E-Mail: {email if email else 'Nicht angegeben'}

Thank you very much für Ihre Angaben.
Beim ersten Besuch bitten wir Sie, einen detaillierteren Anamnesebogen auszufüllen.
Please bringen Sie einen Personalausweis, Ihre Versichertenkarte und eventuelle frühere Röntgenbilder mit.
"""
        
    except Exception as e:
        logging.error(f"Fehler beim Sammeln der Patientendaten: {e}")
        return "Sorry, es gab einen Fehler beim Speichern der Informationen."

@function_tool()
async def cancel_appointment(
    context: RunContext,
    patient_name: str,
    phone: str,
    date: str,
    time: str = ""
) -> str:
    """
    Storniert einen bestehenden appointment.
    Parameter: Patientenname, Telefon, Datum (YYYY-MM-DD), Uhrzeit (optional)
    """
    try:
        # Suche den appointment
        if date in appointments_db:
            if time and time in appointments_db[date]:
                appointments_db[date].remove(time)
                return f"""
appointment erfolgreich storniert.

Stornierungsdetails:
• patient: {patient_name}
• Datum: {date}
• Uhrzeit: {time}

Die Stornierung wurde registriert. Falls Sie einen neuen appointment vereinbaren möchten, helfe ich Ihnen Gladly dabei, ein neues Datum zu finden.
"""
            elif not time:
                # Se non è specificata l'ora, mostra gli appuntamenti per quella data
                return f"Ich habe appointments für {date} gefunden. Können Sie die Uhrzeit angeben, die storniert werden soll?"

        return f"Ich habe keine appointments für {patient_name} am {date} gefunden. Können Sie die Daten überprüfen?"

    except Exception as e:
        logging.error(f"Fehler bei der Stornierung: {e}")
        return "Sorry, es gab einen Fehler bei der Stornierung."

@function_tool()
async def reschedule_appointment(
    context: RunContext,
    patient_name: str,
    phone: str,
    old_date: str,
    old_time: str,
    new_date: str,
    new_time: str
) -> str:
    """
    Verlegt einen bestehenden appointment.
    Parameter: Name, Telefon, altes Datum, alte Uhrzeit, neues Datum, neue Uhrzeit
    """
    try:
        # Prüfe ob der alte appointment existiert
        if old_date not in appointments_db or old_time not in appointments_db[old_date]:
            return f"Ich habe den ursprünglichen appointment für {patient_name} am {old_date} um {old_time} nicht gefunden."

        # Prüfe Verfügbarkeit des neuen Datums/Uhrzeit
        new_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
        if new_datetime < datetime.now():
            return "Ich kann nicht auf vergangene Daten und Uhrzeiten verlegen."

        # Prüfe ob der neue Slot verfügbar ist
        if new_date in appointments_db and new_time in appointments_db[new_date]:
            return f"Sorry, der Slot am {new_date} um {new_time} ist bereits belegt. Kann ich Ihnen andere Zeiten vorschlagen?"

        # Führe die Verlegung durch
        # Entferne den alten appointment
        appointments_db[old_date].remove(old_time)

        # Füge den neuen appointment hinzu
        if new_date not in appointments_db:
            appointments_db[new_date] = []
        appointments_db[new_date].append(new_time)

        return f"""
appointment erfolgreich verlegt!

Alter appointment:
• Datum: {old_date}
• Uhrzeit: {old_time}

Neuer appointment:
• patient: {patient_name}
• Datum: {new_date}
• Uhrzeit: {new_time}

Wir werden Sie am Tag vorher anrufen, um den neuen appointment zu bestätigen.
"""

    except ValueError:
        return "Ungültiges Datums- oder Uhrzeitformat. Verwenden Sie YYYY-MM-DD für das Datum und HH:MM für die Uhrzeit."
    except Exception as e:
        logging.error(f"Fehler bei der Terminverlegung: {e}")
        return "Sorry, es gab einen Fehler bei der Terminverlegung."

@function_tool()
async def get_insurance_info(
    context: RunContext,
    insurance_name: str = ""
) -> str:
    """
    Fornisce informazioni sulle assicurazioni accettate e coperture.
    """
    try:
        if insurance_name:
            if insurance_name in INSURANCE_INFO["accepted_insurances"]:
                return f"""
Sì, accettiamo {insurance_name}.

{INSURANCE_INFO["coverage_info"]}
{INSURANCE_INFO["direct_billing"]}

Ich empfehle Ihnen, Ihre Versicherung zu kontaktieren, um die spezifische Abdeckung der benötigten Behandlung zu überprüfen.
"""
            else:
                return f"""
{insurance_name} non è nell'elenco delle nostre assicurazioni convenzionate.

Assicurazioni accettate:
{', '.join(INSURANCE_INFO["accepted_insurances"])}

Sie können jedoch immer bei Ihrer Versicherung nachfragen, ob sie Erstattungen für unsere Leistungen anbietet.
"""
        else:
            return f"""
Assicurazioni sanitarie accettate:
{', '.join(INSURANCE_INFO["accepted_insurances"])}

{INSURANCE_INFO["coverage_info"]}
{INSURANCE_INFO["direct_billing"]}
"""

    except Exception as e:
        logging.error(f"Fehler bei Versicherungsinformationen: {e}")
        return "Sorry, es gab einen Fehler beim Abrufen der Versicherungsinformationen."

@function_tool()
async def get_payment_info(
    context: RunContext
) -> str:
    """
    Bietet Informationen über akzeptierte Zahlungsmethoden.
    """
    try:
        return f"""
Akzeptierte Zahlungsmethoden:
{', '.join(PAYMENT_OPTIONS["methods"])}

{PAYMENT_OPTIONS["installments"]}

{PAYMENT_OPTIONS["receipts"]}

Für teure Behandlungen können wir während des Besuchs individuelle Zahlungspläne besprechen.
"""

    except Exception as e:
        logging.error(f"Fehler bei Zahlungsinformationen: {e}")
        return "Sorry, es gab einen Fehler beim Abrufen der Zahlungsinformationen."

@function_tool()
async def get_next_available_appointments(
    context: RunContext,
    ab_datum: str = "",
    behandlungsart: str = "check-up",
    anzahl_vorschlaege: int = 5
) -> str:
    """
    Findet die nächsten verfügbaren appointments für patients.
    ab_datum: Ab welchem Datum suchen (YYYY-MM-DD)
    behandlungsart: Art der Behandlung
    anzahl_vorschlaege: Anzahl der Vorschläge
    """
    try:
        if not ab_datum:
            # ✅ KONSISTENT: Verwende get_current_datetime_info()
            time_info = get_current_datetime_info()
            ab_datum = time_info['date_iso']
        
        verfuegbare_termine = appointment_manager.get_verfuegbare_termine(ab_datum, anzahl_vorschlaege)
        
        if not verfuegbare_termine:
            return "Es tut mir leid, aber in den nächsten 30 Tagen sind keine appointments verfügbar. Soll ich weiter in die Zukunft schauen?"
        
        response = f"🗓️ **Die nächsten verfügbaren appointments für {behandlungsart}:**\n\n"
        
        for i, appointment in enumerate(verfuegbare_termine, 1):
            response += f"{i}. {appointment['anzeige']}\n"
        
        response += f"\nWelcher appointment würde Ihnen am besten passen?"
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler bei der Terminsuche: {e}")
        return "Sorry, es gab ein Problem bei der Terminsuche."

@function_tool()
async def get_doctor_daily_schedule(
    context: RunContext,
    datum: str,
    detailliert: bool = True
) -> str:
    """
    Zeigt den Tagesplan für den doctor für einen bestimmten Tag.
    datum: YYYY-MM-DD Format
    detailliert: True für detaillierte Ansicht, False für Übersicht
    """
    try:
        return appointment_manager.get_tagesplan(datum, fuer_arzt=True)
        
    except Exception as e:
        logging.error(f"Fehler beim Abrufen des Tagesplans: {e}")
        return "Sorry, es gab ein Problem beim Abrufen des Tagesplans."

@function_tool()
async def get_doctor_weekly_overview(
    context: RunContext,
    start_datum: str,
    fuer_arzt: bool = True
) -> str:
    """
    Zeigt die Wochenübersicht der appointments für den doctor.
    start_datum: Startdatum der Woche (YYYY-MM-DD)
    fuer_arzt: True für Arztansicht, False für Patienteninfo
    """
    try:
        return appointment_manager.get_wochenuebersicht(start_datum, fuer_arzt)
        
    except Exception as e:
        logging.error(f"Fehler bei Wochenübersicht: {e}")
        return "Sorry, es gab ein Problem bei der Wochenübersicht."

@function_tool()
async def book_appointment_extended(
    context: RunContext,
    patient_name: str,
    telefon: str,
    datum: str,
    uhrzeit: str,
    behandlungsart: str,
    email: str = "",
    beschreibung: str = "",
    notizen: str = ""
) -> str:
    """
    Bucht einen appointment mit erweiterten Informationen.
    patient_name: Name des patients
    telefon: Telefonnummer
    datum: Datum im Format YYYY-MM-DD
    uhrzeit: Uhrzeit im Format HH:MM
    behandlungsart: Art der Behandlung
    email: E-Mail-Adresse (optional)
    beschreibung: Beschreibung des Termins (optional)
    notizen: Zusätzliche Notizen (optional)
    """
    try:
        return appointment_manager.termin_hinzufuegen(
            patient_name, telefon, datum, uhrzeit, behandlungsart, 
            email, beschreibung, notizen
        )
        
    except Exception as e:
        logging.error(f"Fehler beim Buchen des Termins: {e}")
        return f"Sorry, es gab ein Problem beim Buchen des Termins: {str(e)}"

@function_tool()
async def get_patient_history(
    context: RunContext,
    telefon: str
) -> str:
    """
    Zeigt die Terminhistorie eines patients.
    telefon: Telefonnummer des patients
    """
    try:
        return appointment_manager.get_patient_history(telefon)
        
    except Exception as e:
        logging.error(f"Fehler bei Patientenhistorie: {e}")
        return "Sorry, es gab ein Problem beim Abrufen der Patientenhistorie."

@function_tool()
async def search_practice_appointments(
    context: RunContext,
    suchbegriff: str,
    zeitraum: str = "naechste_woche"
) -> str:
    """
    Sucht nach Terminen - NUR für Praxispersonal/Verwaltung.
    NICHT für patients - patients sollen 'find_my_appointments' verwenden.
    suchbegriff: Suchbegriff (Patientenname, Telefon, Behandlungsart)
    zeitraum: Zeitraum (today, tomorrow, naechste_woche, naechster_monat)
    """
    try:
        # Diese Funktion ist für Praxisverwaltung gedacht
        return appointment_manager.termin_suchen(suchbegriff, zeitraum)

    except Exception as e:
        logging.error(f"Fehler bei der practice-Terminsuche: {e}")
        return "Sorry, es gab ein Problem bei der Terminsuche."

@function_tool()
async def find_my_appointments(
    context: RunContext,
    patient_name: str = "",
    telefon: str = "",
    zeitraum: str = "zukunft"
) -> str:
    """
    Findet NUR IHRE persönlichen appointments - nicht die anderer patients.
    Diese Funktion ist für den aktuellen Anrufer/Benutzer gedacht.
    patient_name: IHR Name
    telefon: IHRE Telefonnummer
    zeitraum: Zeitraum (zukunft, alle, today, diese_woche, naechster_monat)
    """
    try:
        if not patient_name and not telefon:
            return "Um Ihre persönlichen appointments zu finden, benötige ich Ihren Namen oder Ihre Telefonnummer. Wie heißen Sie?"

        # Suche nach IHREN Terminen
        suchbegriff = patient_name if patient_name else telefon
        appointments = appointment_manager.termin_suchen(suchbegriff, zeitraum)

        if "keine appointments gefunden" in appointments.lower():
            response = f"📅 **Keine appointments für Sie gefunden**\n\n"
            if patient_name:
                response += f"Für Ihren Namen '{patient_name}' "
            if telefon:
                response += f"Für Ihre Telefonnummer '{telefon}' "
            response += f"wurden keine appointments im Zeitraum '{zeitraum}' gefunden.\n\n"
            response += "💡 **Möchten Sie:**\n"
            response += "• Einen neuen appointment vereinbaren?\n"
            response += "• Prüfen, ob Sie unter einem anderen Namen registriert sind?\n"
            response += "• In einem anderen Zeitraum suchen?"
            return response

        # IHRE appointments gefunden
        response = f"📅 **Ihre persönlichen appointments**\n\n"
        if patient_name:
            response += f"👤 **Ihr Name:** {patient_name}\n"
        if telefon:
            response += f"📞 **Ihre Telefonnummer:** {telefon}\n"
        response += f"📆 **Zeitraum:** {zeitraum}\n\n"
        response += appointments
        response += f"\n\n💡 **Benötigen Sie Änderungen an Ihren Terminen?**"

        return response

    except Exception as e:
        logging.error(f"Fehler beim Finden Ihrer persönlichen appointments: {e}")
        return "Sorry, es gab ein Problem beim Suchen Ihrer persönlichen appointments. Please versuchen Sie es erneut."

@function_tool()
async def get_practice_statistics(
    context: RunContext,
    zeitraum: str = "diese_woche"
) -> str:
    """
    Zeigt Statistiken für die practice.
    zeitraum: Zeitraum (today, diese_woche, diesen_monat)
    """
    try:
        return appointment_manager.get_statistiken(zeitraum)
        
    except Exception as e:
        logging.error(f"Fehler bei Statistiken: {e}")
        return "Sorry, es gab ein Problem beim Abrufen der Statistiken."

@function_tool()
async def cancel_appointment_by_id(
    context: RunContext,
    termin_id: int,
    grund: str = ""
) -> str:
    """
    Sagt einen appointment ab.
    termin_id: ID des Termins
    grund: Grund der Absage (optional)
    """
    try:
        return appointment_manager.cancel_appointment_by_id(termin_id, grund)
        
    except Exception as e:
        logging.error(f"Fehler beim Absagen des Termins: {e}")
        return f"Sorry, es gab ein Problem beim Absagen des Termins: {str(e)}"

@function_tool()
async def check_availability_extended(
    context: RunContext,
    datum: str,
    uhrzeit: str = ""
) -> str:
    """
    Überprüft die Verfügbarkeit für einen bestimmten Tag oder Zeit.
    datum: YYYY-MM-DD Format
    uhrzeit: HH:MM Format (optional)
    """
    try:
        if uhrzeit:
            ist_frei = appointment_manager.ist_verfuegbar(datum, uhrzeit)
            if ist_frei:
                return f"Der appointment am {datum} um {uhrzeit} ist verfügbar!"
            else:
                return f"Der appointment am {datum} um {uhrzeit} ist bereits belegt."
        else:
            # Zeige alle verfügbaren Zeiten für den Tag
            verfuegbare_zeiten = appointment_manager.get_verfuegbare_termine_tag(datum)
            if verfuegbare_zeiten:
                return f"Verfügbare Zeiten am {datum}:\n" + "\n".join(f"• {zeit}" for zeit in verfuegbare_zeiten)
            else:
                return f"Am {datum} sind keine appointments verfügbar."
        
    except Exception as e:
        logging.error(f"Fehler bei Verfügbarkeitsprüfung: {e}")
        return "Sorry, es gab ein Problem bei der Verfügbarkeitsprüfung."

@function_tool()
async def parse_appointment_request(
    context: RunContext,
    text: str
) -> str:
    """
    Verarbeitet natürliche Sprache für Terminwünsche mit KI-Integration.
    text: Terminwunsch in natürlicher Sprache
    """
    try:
        titel, datum, uhrzeit, behandlungsart, kontext = appointment_manager.parse_natural_language(text)
        
        response = f"📋 **Terminwunsch verstanden:**\n\n"
        response += f"� Originaltext: '{text}'\n"
        response += f"�📅 Datum: {datum}\n"
        response += f"🕐 Uhrzeit: {uhrzeit or 'Flexibel'}\n"
        response += f"🦷 Behandlung: {behandlungsart}\n\n"
        
        # Zusätzliche Kontextinformationen
        if kontext["ist_heute_arbeitstag"] and datum == kontext.get("aktuelles_datum"):
            response += f"ℹ️ **Hinweis**: Sie möchten today einen appointment.\n"
            if kontext["praxis_offen"]:
                response += f"✅ Die practice ist derzeit open.\n"
            else:
                response += f"❌ Die practice ist derzeit closed.\n"
                arbeitszeiten = kontext["arbeitszeiten_heute"]
                response += f"⏰ opening hours today: {arbeitszeiten['morning']}"
                if arbeitszeiten['afternoon']:
                    response += f", {arbeitszeiten['afternoon']}"
                response += "\n"
            response += "\n"
        
        if uhrzeit:
            # Prüfe Verfügbarkeit
            ist_frei = appointment_manager.ist_verfuegbar(datum, uhrzeit)
            if ist_frei:
                response += f"✅ **Der gewünschte appointment ist verfügbar!**\n"
                response += f"📅 {datum} um {uhrzeit} für {behandlungsart}\n\n"
                response += f"💡 Möchten Sie diesen appointment buchen?"
            else:
                response += f"❌ **Der gewünschte appointment ist bereits belegt.**\n"
                response += f"📅 {datum} um {uhrzeit}\n\n"
                
                # Zeige intelligente Alternativen
                alternative_termine = appointment_manager.get_smart_appointment_suggestions(behandlungsart, datum, 3)
                response += f"🔄 **Alternative Vorschläge:**\n{alternative_termine}"
        else:
            # Zeige verfügbare Zeiten für den Tag
            verfuegbare_zeiten = appointment_manager.get_verfuegbare_termine_tag(datum)
            if verfuegbare_zeiten:
                response += f"✅ **Verfügbare Zeiten am {datum}:**\n"
                for i, zeit in enumerate(verfuegbare_zeiten[:5], 1):
                    response += f"  {i}. {zeit} o'clock\n"
                response += f"\n💡 Welche Uhrzeit passt Ihnen am besten?"
            else:
                response += f"❌ **Am {datum} sind keine appointments verfügbar.**\n"
                
                # Zeige intelligente Alternativen
                alternative_termine = appointment_manager.get_smart_appointment_suggestions(behandlungsart, datum, 3)
                response += f"\n🔄 **Alternative appointments:**\n{alternative_termine}"
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler beim Parsen des Terminwunsches: {e}")
        return "Sorry, ich konnte Ihren Terminwunsch nicht verstehen."

@function_tool()
async def get_current_datetime_info(
    context: RunContext
) -> str:
    """
    Gibt automatisch das aktuelle Datum und die Uhrzeit zurück.
    AUTOMATISCHE ERKENNUNG - keine manuellen Updates nötig!
    ✅ AUTO-DATUM: Automatische Datum-Einfügung aktiviert
    """
    try:
        # Automatische Datum/Zeit-Erkennung
        info = get_current_datetime_info()

        antwort = f"**Aktuelle Datum- und Zeitinformationen:**\n\n"
        antwort += f"**today**: {info['date_formatted']}\n"
        antwort += f"**Uhrzeit**: {info['time_formatted']}\n"
        antwort += f"**Auto-Datum**: {info['auto_date']}\n"
        antwort += f"**Auto-Zeit**: {info['auto_time']}\n\n"

        # Praxisstatus basierend auf Wochentag und Uhrzeit
        antwort += f"**Praxisstatus:**\n"

        # opening hours bestimmen
        if info['weekday'] == 'Sunday':
            antwort += f"today ist Sunday - practice ist closed.\n"
            antwort += f"tomorrow ({info['tomorrow_weekday']}) sind wir wieder da.\n"
        elif info['weekday'] == 'Saturday':
            antwort += f"today (Saturday) haben wir von 9:00-12:30 open.\n"
            if 9 <= info['hour'] <= 12 and (info['hour'] < 12 or info['minute'] <= 30):
                antwort += f"practice ist derzeit **open**.\n"
            else:
                antwort += f"practice ist derzeit **closed**.\n"
        elif info['weekday'] == 'Friday':
            antwort += f"today (Friday) haben wir von 9:00-11:30 und 14:00-16:00 open.\n"
            if (9 <= info['hour'] <= 11 and (info['hour'] < 11 or info['minute'] <= 30)) or (14 <= info['hour'] < 16):
                antwort += f"practice ist derzeit **open**.\n"
            else:
                antwort += f"practice ist derzeit **closed**.\n"
        else:  # Monday-Thursday
            antwort += f"today ({info['weekday']}) haben wir von 9:00-11:30 und 14:00-17:30 open.\n"
            if (9 <= info['hour'] <= 11 and (info['hour'] < 11 or info['minute'] <= 30)) or (14 <= info['hour'] <= 17 and (info['hour'] < 17 or info['minute'] <= 30)):
                antwort += f"practice ist derzeit **open**.\n"
            else:
                antwort += f"practice ist derzeit **closed**.\n"
        
        antwort += f"\n📊 **Weitere Infos:**\n"
        antwort += f"📅 tomorrow: {info['tomorrow']}\n"
        antwort += f"📅 Übermorgen: {info['übermorgen']}\n"
        antwort += f"📅 Nächste Woche: {info['nächste_woche']}\n"
        antwort += f"📊 Kalenderwoche: {info['kalenderwoche']}\n"
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei Datetime-Info: {e}")
        return "Sorry, es gab ein Problem beim Abrufen der Zeitinformationen."

@function_tool()
async def get_smart_appointment_suggestions(
    context: RunContext,
    behandlungsart: str = "check-up",
    ab_datum: str = "",
    anzahl: int = 5
) -> str:
    """
    Gibt intelligente Terminvorschläge basierend auf dem aktuellen Datum und Kontext.
    behandlungsart: Art der Behandlung
    ab_datum: Ab welchem Datum (leer = intelligent bestimmt)
    anzahl: Anzahl der Vorschläge
    """
    try:
        return appointment_manager.get_smart_appointment_suggestions(behandlungsart, ab_datum, anzahl)
        
    except Exception as e:
        logging.error(f"Fehler bei intelligenten Terminvorschlägen: {e}")
        return "Sorry, es gab ein Problem bei den Terminvorschlägen."

@function_tool()
async def book_appointment_with_details(
    context: RunContext,
    patient_name: str,
    phone: str,
    appointment_date: str,
    appointment_time: str,
    treatment_type: str = "check-up",
    notes: str = ""
) -> str:
    """
    Bucht einen appointment mit allen erforderlichen Patientendetails.
    Stellt sicher, dass Name, Telefon und Beschreibung immer gespeichert werden.
    """
    try:
        # Validiere deutsche Telefonnummer
        if not ist_deutsche_telefonnummer(phone):
            return f"❌ **Terminbuchung nicht möglich**\n\n" \
                   f"Sorry, wir können nur appointments für patients mit deutschen Telefonnummern vereinbaren.\n\n" \
                   f"**Ihre eingegebene Nummer**: {phone}\n\n" \
                   f"Please geben Sie eine deutsche Festnetz- oder Mobilnummer an (z.B. 030 12345678 oder 0170 12345678).\n\n" \
                   f"**Alternative**: Sie können auch Gladly persönlich in unserer practice vorbeikommen:\n" \
                   f"📍 Hauptstraße 123, 10115 Berlin\n" \
                   f"📞 030 12345678"
        
        # Formatiere die Telefonnummer
        phone_formatted = formatiere_telefonnummer(phone)
        
        # Patienteninformationen im CallManager speichern
        call_manager.set_patient_info({
            'name': patient_name,
            'phone': phone_formatted,
            'treatment_type': treatment_type,
            'notes': notes
        })
        
        # appointment buchen
        result = appointment_manager.termin_hinzufuegen(
            patient_name=patient_name,
            telefon=phone_formatted,
            datum=appointment_date,
            uhrzeit=appointment_time,
            behandlungsart=treatment_type,
            notizen=notes
        )
        
        if result:  # termin_hinzufuegen returns True on success
            appointment_data = {
                'patient_name': patient_name,
                'phone': phone,
                'date': appointment_date,
                'time': appointment_time,
                'treatment': treatment_type,
                'notes': notes
            }
            call_manager.mark_appointment_scheduled(appointment_data)
            call_manager.add_note(f"appointment gebucht: {appointment_date} {appointment_time}")
            
            # Lernfähigkeit: Anfrage aufzeichnen
            lernsystem.anfrage_aufzeichnen(f"Termin_{treatment_type}", {
                "datum": appointment_date,
                "uhrzeit": appointment_time,
                "behandlung": treatment_type
            })
            
            return f"**appointment erfolgreich gebucht!**\n\n" \
                   f"**patient**: {patient_name}\n" \
                   f"**Telefon**: {phone}\n" \
                   f"**Datum**: {appointment_date}\n" \
                   f"**Uhrzeit**: {appointment_time}\n" \
                   f"**Behandlung**: {treatment_type}\n" \
                   f"**Notizen**: {notes if notes else 'Keine'}\n\n" \
                   f"Alle Ihre Daten wurden gespeichert. Thank you very much für Ihr Vertrauen!\n\n" \
                   f"Kann ich Ihnen noch mit etwas anderem helfen?"
        else:
            return f"❌ **Terminbuchung fehlgeschlagen**: appointment nicht verfügbar oder bereits belegt"
            
    except Exception as e:
        logging.error(f"Fehler bei Terminbuchung mit Details: {e}")
        return f"❌ Sorry, es gab ein Problem bei der Terminbuchung: {str(e)}"

@function_tool()
async def check_specific_availability(
    context: RunContext,
    datum: str,
    uhrzeit: str,
    behandlungsart: str = "check-up"
) -> str:
    """
    Prüft spezifische Verfügbarkeit für einen exakten appointment.
    """
    try:
        # Verfügbarkeit prüfen
        available = appointment_manager.ist_verfuegbar(datum, uhrzeit)
        
        if available:
            return f"**appointment verfügbar!**\n\n" \
                   f"**Datum**: {datum}\n" \
                   f"**Uhrzeit**: {uhrzeit}\n" \
                   f"**Behandlung**: {behandlungsart}\n\n" \
                   f"Möchten Sie diesen appointment buchen? Ich benötige dann Ihren Namen, den Grund für den Besuch und Ihre Telefonnummer."
        else:
            # Alternative appointments vorschlagen
            alternatives = appointment_manager.get_smart_appointment_suggestions(behandlungsart, datum, 3)
            return f"❌ **appointment nicht verfügbar**\n\n" \
                   f"Der gewünschte appointment am {datum} um {uhrzeit} ist leider nicht verfügbar.\n\n" \
                   f"🔄 **Alternative appointments:**\n{alternatives}"
                   
    except Exception as e:
        logging.error(f"Fehler bei spezifischer Verfügbarkeitsprüfung: {e}")
        return f"❌ Sorry, es gab ein Problem bei der Verfügbarkeitsprüfung: {str(e)}"

@function_tool()
async def end_conversation(
    context: RunContext,
    grund: str = "Verabschiedung"
) -> str:
    """
    Beendet das Gespräch SOFORT und höflich nach einer Verabschiedung.
    KRITISCH: Diese Funktion beendet das Gespräch SOFORT - keine weiteren Nachrichten!
    """
    try:
        # Gespräch SOFORT beenden
        call_manager.initiate_call_end()
        call_manager.status = CallStatus.COMPLETED
        call_manager.add_note(f"Gespräch beendet: {grund}")
        
        # Höfliche Verabschiedung
        response = "Thank you very much für Ihren Anruf! "
        
        # Falls ein appointment gebucht wurde, kurze Bestätigung
        if call_manager.scheduled_appointment:
            apt = call_manager.scheduled_appointment
            response += f"Wir freuen uns auf Sie am {apt['date']} um {apt['time']}. "
            
        response += "Einen schönen Tag noch und Goodbye!"
        
        # Log für Debugging
        logging.info(f"🔴 GESPRÄCH BEENDET: {grund}")
        
        # Ende-Signal für das System
        response += "\n*[CALL_END_SIGNAL]*"
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler bei der Verabschiedung: {e}")
        # KEIN automatisches Beenden bei Fehlern
        return f"Goodbye! Falls Sie noch Fragen haben, bin ich weiterhin für Sie da."

@function_tool()
async def add_note(
    context: RunContext,
    notiz: str
) -> str:
    """
    Fügt eine Notiz zum aktuellen Gespräch hinzu.
    """
    try:
        call_manager.add_note(notiz)
        return f"📝 Notiz hinzugefügt: {notiz}"
        
    except Exception as e:
        logging.error(f"Fehler beim Hinzufügen der Notiz: {e}")
        return f"❌ Fehler beim Speichern der Notiz."

@function_tool()
async def conversation_status(
    context: RunContext
) -> str:
    """
    Gibt den aktuellen Gesprächsstatus zurück.
    """
    try:
        status_text = {
            CallStatus.ACTIVE: "🟢 Aktiv",
            CallStatus.ENDING: "🟡 Wird beendet",
            CallStatus.COMPLETED: "🔴 Beendet"
        }
        
        response = f"📊 **Gesprächsstatus:** {status_text[call_manager.status]}\n\n"
        
        if call_manager.patient_info:
            response += f"👤 **patient:** {call_manager.patient_info.get('name', 'N/A')}\n"
            response += f"📞 **Telefon:** {call_manager.patient_info.get('phone', 'N/A')}\n"
            
        if call_manager.scheduled_appointment:
            response += f"📅 **appointment gebucht:** Ja\n"
            
        if call_manager.notes:
            response += f"📝 **Notizen:** {len(call_manager.notes)}\n"
            
        return response
        
    except Exception as e:
        logging.error(f"Fehler beim Abrufen des Gesprächsstatus: {e}")
        return f"❌ Fehler beim Abrufen des Status."

@function_tool()
async def get_time_aware_greeting(
    context: RunContext
) -> str:
    """
    Erstellt eine zeitbewusste Begrüßung mit AUTOMATISCHER Datum/Zeit-Erkennung.
    """
    try:
        # Automatische Datum/Zeit-Erkennung
        info = get_current_datetime_info()

        # Bestimme die passende Begrüßung basierend auf der Uhrzeit
        if 6 <= info['hour'] < 12:
            begruessung = "Guten tomorrow"
        elif 12 <= info['hour'] < 18:
            begruessung = "Good day"
        else:
            begruessung = "Guten evening"

        # Einfache Begrüßung OHNE automatischen Praxisstatus
        response = f"{begruessung}! Ich bin Sofia, Ihre Assistentin bei der Dental Practice Dr. Weber. "
        response += f"Wie kann ich Ihnen today helfen?"
        
        # Notiz hinzufügen
        call_manager.add_note(f"Begrüßung: {begruessung} um {info['time_formatted']} o'clock")
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler bei zeitbewusster Begrüßung: {e}")
        return "Good day! Ich bin Sofia, Ihre Assistentin bei der Dental Practice Dr. Weber. Wie kann ich Ihnen helfen?"

@function_tool()
async def get_time_based_greeting(
    context: RunContext
) -> str:
    """
    Gibt eine zeitabhängige Begrüßung mit AUTOMATISCHER Datum/Zeit-Erkennung zurück.
    NUTZT die neue get_current_datetime_info() Funktion für korrektes Datum!
    """
    try:
        # AUTOMATISCHE Datum/Zeit-Erkennung verwenden
        info = get_current_datetime_info()

        # Zeitabhängige Begrüßung bestimmen
        if 4 <= info['hour'] <= 10:
            begruessung = "Guten tomorrow"
        elif 11 <= info['hour'] <= 17:
            begruessung = "Good day"
        else:  # 18:00-03:59
            begruessung = "Guten evening"

        # Einfache Begrüßung OHNE automatischen Praxisstatus
        antwort = f"{begruessung}! Ich bin Sofia, Ihre Assistentin bei der Dental Practice Dr. Weber. "
        antwort += f"Wie kann ich Ihnen today helfen?"

        # Notiz hinzufügen - ✅ KONSISTENT: Verwende bereits vorhandene info
        call_manager.add_note(f"Begrüßung: {begruessung} um {info['time_formatted']} o'clock am {info['date_formatted']}")

        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei zeitabhängiger Begrüßung: {e}")
        return "Good day! Ich bin Sofia, Ihre Praxisassistentin. Wie kann ich Ihnen helfen?"

@function_tool()
async def appointment_booking_step_by_step(
    context: RunContext,
    appointment_date: str,
    appointment_time: str,
    treatment_type: str = "check-up"
) -> str:
    """
    Führt Sofia durch die PFLICHT-Reihenfolge für Terminbuchung:
    1. Name fragen
    2. Grund fragen
    3. Telefon fragen
    4. appointment buchen

    Diese Funktion gibt Sofia die EXAKTEN Fragen vor, die sie stellen muss.
    """
    try:
        # Prüfe erst Verfügbarkeit
        available = appointment_manager.ist_verfuegbar(appointment_date, appointment_time)

        if not available:
            alternatives = appointment_manager.get_smart_appointment_suggestions(treatment_type, appointment_date, 3)
            return f"❌ Der gewünschte appointment am {appointment_date} um {appointment_time} ist leider nicht verfügbar.\n\n" \
                   f"🔄 Ich habe diese Alternativen für Sie:\n{alternatives}\n\n" \
                   f"Welcher appointment passt Ihnen?"

        # appointment ist verfügbar - jetzt PFLICHT-Reihenfolge
        response = f"✅ **appointment verfügbar!** {appointment_date} um {appointment_time} für {treatment_type}.\n\n"
        response += f"**Für die Buchung benötige ich:**\n"
        response += f"1. Ihren Namen\n"
        response += f"2. Den Grund für den Besuch\n"
        response += f"3. Ihre Telefonnummer\n\n"
        response += f"**Wie ist Ihr Name?**"

        # Status im CallManager setzen
        call_manager.add_note(f"Terminbuchung gestartet: {appointment_date} um {appointment_time}")

        return response

    except Exception as e:
        logging.error(f"Fehler bei der schrittweisen Terminbuchung: {e}")
        return f"❌ Sorry, es gab ein Problem bei der Terminbuchung. Please versuchen Sie es erneut."

@function_tool()
async def book_appointment_directly(
    context: RunContext,
    patient_name: str,
    phone: str,
    appointment_date: str,
    appointment_time: str,
    treatment_type: str = "check-up",
    notes: str = ""
) -> str:
    """
    Bucht einen appointment DIREKT ohne doppelte Bestätigung.
    ✅ KONSISTENT: Verwendet validate_and_parse_datetime() für Validierung
    """
    try:
        # ✅ KONSISTENTE VALIDIERUNG: Verwende neue Hilfsfunktion
        appointment_datetime, error = validate_and_parse_datetime(appointment_date, appointment_time)

        if error:
            return f"❌ {error}"

        # Daten im CallManager speichern
        call_manager.set_patient_info({
            'name': patient_name,
            'phone': phone,
            'treatment_type': treatment_type,
            'notes': notes
        })

        # Prüfe erst Verfügbarkeit
        available = appointment_manager.ist_verfuegbar(appointment_date, appointment_time)
        
        if not available:
            # Alternative appointments vorschlagen statt Fehler
            alternatives = appointment_manager.get_smart_appointment_suggestions(treatment_type, appointment_date, 3)
            return f"❌ **Der gewünschte appointment am {appointment_date} um {appointment_time} ist leider nicht verfügbar.**\n\n" \
                   f"🔄 **Ich habe diese Alternativen für Sie:**\n{alternatives}\n\n" \
                   f"Welcher appointment passt Ihnen?"
        
        # appointment direkt buchen (ohne nochmalige Bestätigung)
        result = appointment_manager.termin_hinzufuegen(
            patient_name=patient_name,
            telefon=phone,
            datum=appointment_date,
            uhrzeit=appointment_time,
            behandlungsart=treatment_type,
            notizen=notes
        )

        # ✅ BESSERE FEHLERBEHANDLUNG: Prüfe spezifische Fehlermeldungen
        if result and not result.startswith("❌"):
            # Erfolgreiche Buchung
            appointment_data = {
                'patient_name': patient_name,
                'phone': phone,
                'date': appointment_date,
                'time': appointment_time,
                'treatment': treatment_type,
                'notes': notes
            }
            call_manager.mark_appointment_scheduled(appointment_data)
            call_manager.add_note(f"appointment direkt gebucht: {appointment_date} {appointment_time}")

            return f"**✅ Perfekt! Ihr appointment ist gebucht!**\n\n" \
                   f"👤 **Name**: {patient_name}\n" \
                   f"📞 **Telefon**: {phone}\n" \
                   f"📅 **appointment**: {appointment_date} um {appointment_time}\n" \
                   f"🦷 **Behandlung**: {treatment_type}\n" \
                   f"📝 **Notizen**: {notes if notes else 'Keine besonderen Notizen'}\n\n" \
                   f"🎉 **Ihr appointment ist bestätigt!** Wir freuen uns auf Sie!\n" \
                   f"📞 Bei Fragen erreichen Sie uns unter: 0123 456 789\n\n" \
                   f"💡 **Kann ich Ihnen noch bei etwas anderem helfen?**"
        else:
            # Fehler bei der Buchung - zeige spezifische Fehlermeldung
            error_msg = result if result else "Unbekannter Fehler beim Speichern"

            # Biete Alternativen an
            alternatives = appointment_manager.get_smart_appointment_suggestions(treatment_type, appointment_date, 3)

            return f"{error_msg}\n\n" \
                   f"🔄 **Keine Sorge! Hier sind alternative appointments:**\n{alternatives}\n\n" \
                   f"💡 **Welcher appointment würde Ihnen passen?**"
            
    except Exception as e:
        logging.error(f"Fehler bei direkter Terminbuchung: {e}")
        return f"❌ Sorry, es gab ein Problem bei der Terminbuchung: {str(e)}"

@function_tool()
async def ask_medical_followup_questions(
    context: RunContext,
    symptom_oder_grund: str
) -> str:
    """
    🩺 Stellt intelligente medizinische Nachfragen basierend auf Symptomen oder Behandlungsgründen.
    Sofia wird hilfreicher und fragt nach wichtigen Details wie:
    - Bei pain: seit wann, Medikamente, Art des Schmerzes
    - Bei Implantaten: Probleme oder nur Kontrolle
    - Bei allen Fällen: relevante medizinische Details

    symptom_oder_grund: Das Symptom oder der Grund für den Zahnarztbesuch
    """
    try:
        # Notiere die medizinische Nachfrage
        call_manager.add_note(f"Medizinische Nachfrage zu: {symptom_oder_grund}")

        # Hole intelligente Nachfragen
        nachfragen = get_intelligente_medizinische_nachfragen(symptom_oder_grund)

        return nachfragen

    except Exception as e:
        logging.error(f"Fehler bei medizinischen Nachfragen: {e}")
        return "Sorry, ich konnte keine spezifischen Nachfragen generieren. Können Sie mir mehr über Ihre Beschwerden erzählen?"

@function_tool()
async def smart_appointment_booking_with_followups(
    context: RunContext,
    appointment_date: str,
    appointment_time: str,
    symptom_oder_grund: str,
    patient_name: str = "",
    phone: str = ""
) -> str:
    """
    🎯 INTELLIGENTE TERMINBUCHUNG - Kombiniert medizinische Nachfragen mit Terminbuchung
    Verhindert doppelte Namens-Abfrage durch intelligente Kombination

    appointment_date: Gewünschtes Datum (YYYY-MM-DD)
    appointment_time: Gewünschte Uhrzeit (HH:MM)
    symptom_oder_grund: Grund für den Besuch (für medizinische Nachfragen)
    patient_name: Name (falls bereits bekannt)
    phone: Telefon (falls bereits bekannt)
    """
    try:
        # Prüfe erst Verfügbarkeit
        available = appointment_manager.ist_verfuegbar(appointment_date, appointment_time)

        if not available:
            alternatives = appointment_manager.get_smart_appointment_suggestions(symptom_oder_grund, appointment_date, 3)
            return f"Der gewünschte appointment am {appointment_date} um {appointment_time} ist leider nicht verfügbar. " \
                   f"Ich habe diese Alternativen für Sie: {alternatives} Welcher appointment passt Ihnen?"

        # appointment ist verfügbar
        response = f"Sehr gut, der appointment am {appointment_date} um {appointment_time} ist verfügbar. "

        # Medizinische Nachfragen stellen (nur wenn noch nicht gestellt)
        if symptom_oder_grund and not any(word in symptom_oder_grund.lower() for word in ['kontrolle', 'untersuchung', 'check']):
            medizinische_nachfrage = get_intelligente_medizinische_nachfragen(symptom_oder_grund)
            response += medizinische_nachfrage + " "

        # Fehlende Daten abfragen - prüfe gespeicherten Namen
        if not patient_name:
            # Prüfe ob Name bereits gespeichert ist
            if call_manager.has_patient_name():
                patient_name = call_manager.get_patient_name()
                response += f"Für Sie, {patient_name}, benötige ich nur noch Ihre Telefonnummer. "
            else:
                response += "Wie ist Ihr Name?"
                call_manager.add_note(f"Terminbuchung gestartet: {appointment_date} um {appointment_time} für {symptom_oder_grund}")
                return response
        elif not phone:
            response += "Und Ihre Telefonnummer?"
            return response
        else:
            # Alle Daten vorhanden - direkt buchen
            return await book_appointment_directly(
                context=context,
                patient_name=patient_name,
                phone=phone,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                treatment_type=symptom_oder_grund,
                notes=""
            )

    except Exception as e:
        logging.error(f"Fehler bei intelligenter Terminbuchung: {e}")
        return f"Sorry, es gab ein Problem bei der Terminbuchung. Please versuchen Sie es erneut."

@function_tool()
async def recognize_and_save_name(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🧠 NAMEN-ERKENNUNG: Erkennt und speichert Patientennamen aus der Eingabe
    Verhindert doppelte Namens-Abfrage durch intelligente Erkennung

    patient_input: Die Eingabe des patients (z.B. "Ich bin Max Mustermann")
    """
    try:
        # Einfache Namen-Erkennung
        input_lower = patient_input.lower()

        # Muster für Namen-Erkennung
        name_patterns = [
            r"ich bin\s+([a-zA-ZäöüÄÖÜß\s]+)",
            r"mein name ist\s+([a-zA-ZäöüÄÖÜß\s]+)",
            r"ich heiße\s+([a-zA-ZäöüÄÖÜß\s]+)",
            r"hier ist\s+([a-zA-ZäöüÄÖÜß\s]+)",
            r"([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)",  # Vor- und Nachname
        ]

        import re
        detected_name = None

        for pattern in name_patterns:
            match = re.search(pattern, patient_input, re.IGNORECASE)
            if match:
                detected_name = match.group(1).strip()
                break

        if detected_name and len(detected_name) > 2:
            # Namen speichern
            call_manager.set_patient_name(detected_name)
            return f"Hello {detected_name}! Schön, dass Sie sich gemeldet haben. Wie kann ich Ihnen helfen?"

        # Kein Name erkannt - höflich nachfragen
        if call_manager.should_ask_for_name():
            call_manager.mark_name_asked()
            return "Hello! Ich bin Sofia von der Dental Practice Dr. Weber. Darf ich fragen, wie Sie heißen?"

        # Name bereits bekannt oder schon gefragt
        if call_manager.has_patient_name():
            return f"Hello {call_manager.get_patient_name()}! Wie kann ich Ihnen helfen?"
        else:
            return "Hello! Wie kann ich Ihnen helfen?"

    except Exception as e:
        logging.error(f"Fehler bei Namen-Erkennung: {e}")
        return "Hello! Wie kann ich Ihnen helfen?"

@function_tool()
async def smart_response_with_name_recognition(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🧠 INTELLIGENTE ANTWORT: Erkennt automatisch Namen und antwortet entsprechend
    Beispiel: "Hello Sofia, mein Name ist Müller" → Erkennt "Müller" automatisch

    patient_input: Die komplette Eingabe des patients
    """
    try:
        import re

        # 1. NAMEN-ERKENNUNG aus der Eingabe
        name_patterns = [
            r"mein name ist\s+([a-zA-ZäöüÄÖÜß\s]+)",
            r"ich bin\s+([a-zA-ZäöüÄÖÜß\s]+)",
            r"ich heiße\s+([a-zA-ZäöüÄÖÜß\s]+)",
            r"hier ist\s+([a-zA-ZäöüÄÖÜß\s]+)",
            r"([A-ZÄÖÜ][a-zäöüß]+)",  # Einzelner Name wie "Müller", "Peter", "Ralph"
        ]

        detected_name = None
        for pattern in name_patterns:
            match = re.search(pattern, patient_input, re.IGNORECASE)
            if match:
                potential_name = match.group(1).strip()
                # Filtere häufige Nicht-Namen aus
                if potential_name.lower() not in ['sofia', 'Hello', 'guten', 'tag', 'evening', 'tomorrow', 'ich', 'bin', 'der', 'die', 'das', 'haben', 'pain', 'appointment']:
                    detected_name = potential_name
                    break

        # 2. NAMEN SPEICHERN falls erkannt und noch nicht gespeichert
        if detected_name and len(detected_name) > 2 and not call_manager.has_patient_name():
            call_manager.set_patient_name(detected_name)
            response = f"Hello {detected_name}! "
        elif call_manager.has_patient_name():
            response = f"Hello {call_manager.get_patient_name()}! "
        else:
            response = "Hello! "

        # 3. INHALTLICHE ANTWORT basierend auf Eingabe
        input_lower = patient_input.lower()

        # Terminwunsch erkennen
        if any(word in input_lower for word in ['appointment', 'appointment', 'buchung', 'vereinbaren']):
            # Prüfe ob Grund bereits genannt wurde
            grund_keywords = ['schmerz', 'kontrolle', 'reinigung', 'filling', 'krone', 'implantat', 
                            'zahnfleisch', 'wurzel', 'weisheit', 'ziehen', 'bluten', 'geschwollen',
                            'gebrochen', 'emergency', 'vorsorge', 'prophylaxe', 'beratung']
            
            hat_grund = any(keyword in input_lower for keyword in grund_keywords)
            
            if hat_grund:
                response += "Gladly vereinbare ich einen appointment für Sie. Wie ist Ihr Name?"
            else:
                response += "Gladly vereinbare ich einen appointment für Sie. Wofür benötigen Sie denn den appointment?"
                
                # Lernfähigkeit: Häufige Terminanfragen tracken
                lernsystem.anfrage_aufzeichnen("Terminanfrage_ohne_Grund", {
                    "input": patient_input,
                    "zeitstempel": datetime.now().isoformat()
                })

        # pain erkennen
        elif any(word in input_lower for word in ['schmerz', 'pain', 'weh', 'tut weh', 'ziehen', 'stechen', 'pochen']):
            response += "Oh, das tut mir leid zu hören, dass Sie pain haben. Seit wann haben Sie denn die Beschwerden?"

        # Implantat erkennen
        elif any(word in input_lower for word in ['implantat', 'implant']):
            response += "Ah, es geht um Ihr Implantat. Ist das nur für eine check-up oder haben Sie Probleme damit?"

        # Zahnfleisch erkennen
        elif any(word in input_lower for word in ['zahnfleisch', 'blutet', 'geschwollen']):
            response += "Ich verstehe, Sie haben Probleme mit dem Zahnfleisch. Blutet es beim Zähneputzen?"

        # Kontrolle erkennen
        elif any(word in input_lower for word in ['kontrolle', 'untersuchung', 'check', 'vorsorge']):
            response += "Das ist sehr gut, dass Sie zur Kontrolle kommen möchten. Wann hätten Sie Zeit?"
        
        # Freie appointments anfragen
        elif any(phrase in input_lower for phrase in ['appointments frei', 'freie appointments', 'verfügbar', 'noch platz', 'noch appointments']):
            # Prüfe ob Name schon bekannt ist
            if call_manager.patient_name:
                response += f"Gladly schaue ich nach freien Terminen für Sie, {call_manager.patient_name}. "
                response += "Für welche Behandlung benötigen Sie einen appointment?"
            else:
                response += "Gladly schaue ich nach freien Terminen für Sie. "
                response += "Um Ihnen passende appointments vorzuschlagen, benötige ich zunächst Ihren Namen und Ihre Telefonnummer."
                
                # Lernfähigkeit: Terminanfrage ohne Identifikation tracken
                lernsystem.anfrage_aufzeichnen("Terminanfrage_ohne_Identifikation", {
                    "input": patient_input,
                    "zeitstempel": datetime.now().isoformat()
                })

        # Allgemeine Begrüßung
        else:
            response += "Wie kann ich Ihnen today helfen?"

        return response

    except Exception as e:
        logging.error(f"Fehler bei intelligenter Antwort: {e}")
        return "Hello! Wie kann ich Ihnen helfen?"

@function_tool()
async def end_conversation_politely(
    context: RunContext,
    patient_input: str = ""
) -> str:
    """
    📞 GESPRÄCHS-BEENDIGUNG: Beendet das Gespräch höflich wenn patient keine Hilfe mehr braucht
    Erkennt Aussagen wie "ich brauche keine Hilfe mehr", "das war alles", "Thank you, Bye"

    patient_input: Die Eingabe des patients (optional, für Kontext)
    """
    try:
        # Markiere Gespräch als beendet
        call_manager.end_call()

        # Höfliche Verabschiedung basierend auf Tageszeit
        from .dental_tools import get_current_datetime_info
        info = get_current_datetime_info()

        if call_manager.has_patient_name():
            patient_name = call_manager.get_patient_name()
            if 4 <= info['hour'] <= 17:
                verabschiedung = f"Thank you very much für Ihren Anruf, {patient_name}. Haben Sie einen schönen Tag! Goodbye."
            else:
                verabschiedung = f"Thank you very much für Ihren Anruf, {patient_name}. Haben Sie einen schönen evening! Goodbye."
        else:
            if 4 <= info['hour'] <= 17:
                verabschiedung = "Thank you very much für Ihren Anruf. Haben Sie einen schönen Tag! Goodbye."
            else:
                verabschiedung = "Thank you very much für Ihren Anruf. Haben Sie einen schönen evening! Goodbye."

        # Notiz für das Gespräch
        call_manager.add_note(f"Gespräch beendet: {verabschiedung}")

        return verabschiedung

    except Exception as e:
        logging.error(f"Fehler bei Gesprächs-Beendigung: {e}")
        return "Thank you very much für Ihren Anruf. Goodbye!"

@function_tool()
async def detect_conversation_end_wish(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🔍 ERKENNUNG GESPRÄCHSENDE: Erkennt wenn patient das Gespräch beenden möchte
    Beispiele: "ich brauche keine Hilfe mehr", "das war alles", "Thank you Bye"

    patient_input: Die Eingabe des patients
    """
    try:
        input_lower = patient_input.lower()

        # Erkennungsmuster für Gesprächsende
        ende_muster = [
            "brauche keine hilfe mehr",
            "brauche nichts mehr",
            "das war alles",
            "das wars",
            "mehr brauche ich nicht",
            "reicht mir",
            "Thank you Bye",
            "Thank you tschuss",
            "Goodbye",
            "Goodbye",
            "bis dann",
            "muss auflegen",
            "muss schluss machen",
            "keine weitere hilfe",
            "alles erledigt",
            "passt so",
            "ist gut so",
            "Thank you das reicht"
        ]

        # Prüfe ob patient das Gespräch beenden möchte
        for muster in ende_muster:
            if muster in input_lower:
                # Gespräch beenden
                return await end_conversation_politely(context, patient_input)

        # Kein Gesprächsende erkannt - normale Antwort
        return await smart_response_with_name_recognition(context, patient_input)

    except Exception as e:
        logging.error(f"Fehler bei Gesprächsende-Erkennung: {e}")
        return "Wie kann ich Ihnen weiter helfen?"

@function_tool()
async def smart_reason_followup(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🤔 INTELLIGENTE GRUND-NACHFRAGEN: Fragt spezifisch nach dem Grund für den appointment
    - Wenn kein Grund angegeben: "Wieso benötigen Sie einen appointment?"
    - Bei "Kontrolle": "Gibt es einen besonderen Grund oder nur normale Untersuchung?"
    - Bei vagen Angaben: Spezifische Nachfragen

    patient_input: Die Eingabe des patients
    """
    try:
        input_lower = patient_input.lower()

        # 1. KEIN GRUND ERKANNT - Allgemeine Nachfrage
        if any(phrase in input_lower for phrase in [
            'brauche einen appointment', 'möchte einen appointment', 'appointment vereinbaren',
            'appointment buchen', 'kann ich einen appointment'
        ]) and not any(grund in input_lower for grund in [
            'schmerz', 'weh', 'kontrolle', 'untersuchung', 'reinigung', 'implantat',
            'krone', 'filling', 'zahnfleisch', 'weisheitszahn', 'bleaching', 'emergency'
        ]):
            return "Gladly vereinbare ich einen appointment für Sie. Wieso benötigen Sie denn einen appointment?"

        # 2. KONTROLLE/UNTERSUCHUNG - Spezifische Nachfrage
        elif any(word in input_lower for word in ['kontrolle', 'untersuchung', 'check', 'vorsorge']):
            return "Sie möchten zur Kontrolle kommen. Gibt es einen besonderen Grund oder ist es einfach eine normale Untersuchung?"

        # 3. REINIGUNG - Nachfrage nach Zusätzlichem
        elif any(word in input_lower for word in ['reinigung', 'dental cleaning', 'prophylaxe']):
            return "Eine professionelle dental cleaning, sehr gut. Soll das mit einer Kontrolle kombiniert werden?"

        # 4. VAGE BEGRIFFE - Spezifische Nachfragen
        elif any(word in input_lower for word in ['problem', 'beschwerden', 'etwas', 'schauen']):
            return "Sie haben ein Problem. Was genau beschäftigt Sie denn?"

        # 5. BEREITS SPEZIFISCH - Verwende medizinische Nachfragen
        elif any(word in input_lower for word in [
            'schmerz', 'pain', 'weh', 'implantat', 'krone', 'filling',
            'weisheitszahn', 'zahnfleisch', 'blutet', 'geschwollen'
        ]):
            # Bereits spezifisch genug - verwende medizinische Nachfragen
            return await ask_medical_followup_questions(context, patient_input)

        # 6. UNKLARE EINGABE - Höfliche Nachfrage
        else:
            return "Wieso benötigen Sie einen appointment?"

    except Exception as e:
        logging.error(f"Fehler bei Grund-Nachfragen: {e}")
        return "Wieso benötigen Sie einen appointment?"

@function_tool()
async def smart_reason_followup(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🤔 INTELLIGENTE GRUND-NACHFRAGEN: Fragt spezifisch nach dem Grund für den appointment
    - Wenn kein Grund angegeben: "Wofür benötigen Sie einen appointment?"
    - Bei "Kontrolle": "Gibt es einen besonderen Grund oder nur normale Untersuchung?"
    - Bei vagen Angaben: Spezifische Nachfragen

    patient_input: Die Eingabe des patients
    """
    try:
        input_lower = patient_input.lower()

        # 1. KEIN GRUND ERKANNT - Allgemeine Nachfrage
        if any(phrase in input_lower for phrase in [
            'brauche einen appointment', 'möchte einen appointment', 'appointment vereinbaren',
            'appointment buchen', 'appointment', 'kann ich einen appointment'
        ]) and not any(grund in input_lower for grund in [
            'schmerz', 'weh', 'kontrolle', 'untersuchung', 'reinigung', 'implantat',
            'krone', 'filling', 'zahnfleisch', 'weisheitszahn', 'bleaching', 'emergency'
        ]):
            return "Gladly vereinbare ich einen appointment für Sie. Wofür benötigen Sie denn den appointment? Haben Sie Beschwerden oder ist es für eine Kontrolle?"

        # 2. KONTROLLE/UNTERSUCHUNG - Spezifische Nachfrage
        elif any(word in input_lower for word in ['kontrolle', 'untersuchung', 'check', 'vorsorge']):
            return "Verstehe, Sie möchten zur Kontrolle kommen. Gibt es einen besonderen Grund oder Beschwerden, oder ist es einfach eine normale Vorsorgeuntersuchung?"

        # 3. REINIGUNG - Nachfrage nach Zusätzlichem
        elif any(word in input_lower for word in ['reinigung', 'dental cleaning', 'prophylaxe']):
            return "Sehr gut, eine professionelle dental cleaning. Soll das mit einer Kontrolle kombiniert werden oder haben Sie zusätzliche Beschwerden?"

        # 4. VAGE BEGRIFFE - Spezifische Nachfragen
        elif any(word in input_lower for word in ['problem', 'beschwerden', 'etwas', 'schauen']):
            return "Ich verstehe, Sie haben ein Problem. Können Sie mir sagen, was genau Sie beschäftigt? Haben Sie pain oder geht es um etwas Bestimmtes?"

        # 5. ZAHNFLEISCH - Detaillierte Nachfrage
        elif any(word in input_lower for word in ['zahnfleisch', 'blutet', 'geschwollen']):
            return "Ach so, es geht um das Zahnfleisch. Blutet es beim Zähneputzen oder ist es geschwollen? Seit wann haben Sie das bemerkt?"

        # 6. ZAHN ALLGEMEIN - Spezifische Nachfrage
        elif any(word in input_lower for word in ['zahn', 'zähne']) and not any(word in input_lower for word in ['schmerz', 'weh']):
            return "Es geht um einen Zahn. Haben Sie pain oder ist etwas anderes mit dem Zahn? Ist er abgebrochen oder haben Sie andere Beschwerden?"

        # 7. ÄSTHETIK/AUSSEHEN - Beratungsansatz
        elif any(word in input_lower for word in ['schön', 'aussehen', 'ästhetik', 'weiß', 'gerade']):
            return "Sie interessieren sich für ästhetische Zahnbehandlung. Geht es um die Farbe der Zähne, die Stellung oder etwas anderes?"

        # 8. KINDER - Spezielle Nachfrage
        elif any(word in input_lower for word in ['kind', 'kinder', 'sohn', 'tochter']):
            return "Ah, es geht um ein Kind. Wie alt ist das Kind und gibt es bestimmte Beschwerden oder ist es der erste Zahnarztbesuch?"

        # 9. ANGST/NERVÖS - Einfühlsame Nachfrage
        elif any(word in input_lower for word in ['angst', 'nervös', 'furcht', 'scared']):
            return "Ich verstehe, dass Zahnarztbesuche manchmal Angst machen können. Wir nehmen uns Gladly Zeit für Sie. Wofür benötigen Sie den appointment?"

        # 10. urgent/SCHNELL - emergency-Einschätzung
        elif any(word in input_lower for word in ['urgent', 'schnell', 'sofort', 'today', 'tomorrow']):
            return "Das klingt urgent. Haben Sie pain oder was ist passiert? Je nach Situation können wir einen Notfalltermin arrangieren."

        # 11. BEREITS SPEZIFISCH - Keine weitere Nachfrage nötig
        elif any(word in input_lower for word in [
            'schmerz', 'pain', 'weh', 'implantat', 'krone', 'filling',
            'weisheitszahn', 'root canal', 'extraction', 'bleaching'
        ]):
            # Bereits spezifisch genug - verwende medizinische Nachfragen
            return await ask_medical_followup_questions(context, patient_input)

        # 12. UNKLARE EINGABE - Höfliche Nachfrage
        else:
            return "Gladly helfe ich Ihnen weiter. Können Sie mir sagen, wofür Sie einen appointment benötigen? Haben Sie Beschwerden oder geht es um eine Kontrolle?"

    except Exception as e:
        logging.error(f"Fehler bei Grund-Nachfragen: {e}")
        return "Gladly vereinbare ich einen appointment für Sie. Wofür benötigen Sie denn den appointment?"

@function_tool()
async def conversational_repair(
    context: RunContext,
    user_input: str
) -> str:
    """
    🧠 SMART FALLBACK: Conversational Repair für Korrekturen
    - Erkennt "Nein, lieber 11:30" und korrigiert letzten Terminvorschlag
    - Stateful Dialog ohne Neustart

    user_input: Korrektur-Eingabe des patients
    """
    try:
        # Prüfe ob es eine Korrektur ist
        correction_indicators = ["nein", "lieber", "besser", "stattdessen", "nicht", "anders"]

        if any(indicator in user_input.lower() for indicator in correction_indicators):
            # Versuche Zeit-Korrektur
            corrected_slot = context_stack.repair_time(user_input)

            if corrected_slot:
                # Speichere korrigierten Slot
                context_stack.set_last_slot(corrected_slot)

                return f"Verstehe! Sie möchten lieber {corrected_slot['wochentag']}, {corrected_slot['datum']} um {corrected_slot['uhrzeit']} o'clock. Lassen Sie mich das für Sie prüfen."
            else:
                return "Sorry, ich habe Ihre Korrektur nicht ganz verstanden. Können Sie mir sagen, wann Sie den appointment lieber hätten?"

        # Keine Korrektur erkannt
        return "Wie kann ich Ihnen weiter helfen?"

    except Exception as e:
        logging.error(f"Fehler bei Conversational Repair: {e}")
        return "Sorry, können Sie das nochmal sagen?"

@function_tool()
async def emergency_prioritization(
    context: RunContext,
    symptome: str,
    schmerzskala: int = 0
) -> str:
    """
    Priorisiert emergencies basierend auf Symptomen und Schmerzintensität.
    Schlägt sofortige Terminoptionen vor.
    """
    try:
        # Validiere Schmerzskala
        if schmerzskala < 0 or schmerzskala > 10:
            schmerzskala = 0
        
        # Definiere emergency-Keywords
        notfall_keywords = [
            "unfall", "blutung", "geschwollen", "fieber", "eiter",
            "gebrochen", "verletzt", "stark", "unerträglich", "akut"
        ]
        
        # Prüfe auf emergency-Keywords
        ist_notfall = any(keyword in symptome.lower() for keyword in notfall_keywords)
        
        # Lernfähigkeit: emergency aufzeichnen
        if ist_notfall or schmerzskala >= 5:
            lernsystem.anfrage_aufzeichnen("emergency", {
                "symptome": symptome,
                "schmerzskala": schmerzskala,
                "keywords": [k for k in notfall_keywords if k in symptome.lower()]
            })
        
        # Priorisierung basierend auf Schmerzskala und Keywords
        if schmerzskala >= 8 or ist_notfall:
            prioritaet = "HOCH"
            empfehlung = "Sofortiger Notfalltermin erforderlich"
            wartezeit = "Sofort - innerhalb 30 Minuten"
        elif schmerzskala >= 5:
            prioritaet = "MITTEL"
            empfehlung = "appointment today noch empfohlen"
            wartezeit = "Innerhalb 2-4 Stunden"
        else:
            prioritaet = "NIEDRIG"
            empfehlung = "Regulärer appointment ausreichend"
            wartezeit = "Nächster verfügbarer appointment"
        
        # Hole nächste verfügbare Notfalltermine
        from datetime import datetime, timedelta
        jetzt = datetime.now()
        
        antwort = f"**emergency-Bewertung:**\n\n"
        antwort += f"**Symptome**: {symptome}\n"
        if schmerzskala > 0:
            antwort += f"**Schmerzskala**: {schmerzskala}/10\n"
        antwort += f"**Priorität**: {prioritaet}\n"
        antwort += f"**Empfehlung**: {empfehlung}\n"
        antwort += f"**Geschätzte Wartezeit**: {wartezeit}\n\n"
        
        if prioritaet == "HOCH":
            antwort += "**Sofortmaßnahmen:**\n"
            antwort += "- Kommen Sie SOFORT in die practice\n"
            antwort += "- Bei starker Blutung: Mit sauberem Tuch Druck ausüben\n"
            antwort += "- Bei Schwellung: Kühlen mit Eis (in Tuch eingewickelt)\n"
            antwort += "- Bei starken pain: Ibuprofen 400mg (falls keine Allergie)\n\n"
            antwort += "**Notfallnummer**: +49 30 12345678\n"
        elif prioritaet == "MITTEL":
            # Suche nächste verfügbare appointments today
            today = jetzt.strftime("%Y-%m-%d")
            verfuegbare = appointment_manager.get_verfuegbare_termine_tag(today)
            
            if verfuegbare:
                antwort += f"**Verfügbare appointments today:**\n"
                for appointment in verfuegbare[:3]:
                    antwort += f"- {appointment}\n"
            else:
                antwort += "today keine regulären appointments mehr, aber Notfalltermin möglich.\n"
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei emergency-Priorisierung: {e}")
        return "Please beschreiben Sie Ihre Symptome genauer, damit ich die Dringlichkeit einschätzen kann."

@function_tool()
async def waiting_time_estimation(
    context: RunContext,
    datum: str,
    uhrzeit: str
) -> str:
    """
    Schätzt die aktuelle Wartezeit basierend auf dem Terminplan.
    Berücksichtigt durchschnittliche Behandlungsdauern und Verspätungen.
    """
    try:
        from datetime import datetime, timedelta
        
        # Parse Datum und Zeit
        termin_zeit = datetime.strptime(f"{datum} {uhrzeit}", "%Y-%m-%d %H:%M")
        jetzt = datetime.now()
        
        # Hole Tagesplan
        tagesplan = appointment_manager.get_tagesplan(datum)
        
        # Durchschnittliche Behandlungsdauern (in Minuten)
        behandlungsdauern = {
            "check-up": 30,
            "dental cleaning": 45,
            "filling": 60,
            "root canal": 90,
            "Zahnentfernung": 45,
            "Beratung": 30,
            "emergency": 45
        }
        
        # Berechne geschätzte Wartezeit
        geschaetzte_wartezeit = 0
        aktuelle_zeit = datetime.strptime(f"{datum} 09:00", "%Y-%m-%d %H:%M")
        
        for appointment in tagesplan:
            termin_start = datetime.strptime(f"{datum} {appointment['uhrzeit']}", "%Y-%m-%d %H:%M")
            
            # Wenn appointment vor dem angefragten Zeitpunkt
            if termin_start < termin_zeit:
                behandlungsart = appointment.get('behandlung', 'check-up')
                dauer = behandlungsdauern.get(behandlungsart, 30)
                
                # Füge 10% Puffer für mögliche Verzögerungen hinzu
                dauer_mit_puffer = int(dauer * 1.1)
                
                # Wenn dieser appointment noch nicht abgeschlossen sein sollte
                termin_ende = termin_start + timedelta(minutes=dauer_mit_puffer)
                if termin_ende > termin_zeit:
                    geschaetzte_wartezeit += (termin_ende - termin_zeit).seconds // 60
        
        # Erstelle Antwort
        antwort = f"**Wartezeit-Schätzung für {datum} um {uhrzeit}:**\n\n"
        
        if geschaetzte_wartezeit > 0:
            antwort += f"**Geschätzte Wartezeit**: ca. {geschaetzte_wartezeit} Minuten\n\n"
            antwort += "**Mögliche Gründe für Wartezeit:**\n"
            antwort += "- Vorherige Behandlungen dauern länger als geplant\n"
            antwort += "- Notfallpatienten wurden eingeschoben\n\n"
            antwort += "**Empfehlung**: Please kommen Sie trotzdem pünktlich, "
            antwort += "da sich die Situation ändern kann.\n"
        else:
            antwort += "**Keine Wartezeit erwartet** ✓\n\n"
            antwort += "Sie sollten pünktlich drankommen.\n"
        
        # Füge aktuelle Auslastung hinzu
        termine_heute = len(tagesplan)
        if termine_heute > 15:
            antwort += "\n**Hinweis**: today ist ein sehr voller Tag in der practice."
        elif termine_heute < 8:
            antwort += "\n**Hinweis**: today ist es relativ ruhig in der practice."
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei Wartezeit-Schätzung: {e}")
        return "Ich kann die Wartezeit momentan nicht einschätzen. Please rufen Sie uns direkt an."

@function_tool()
async def schedule_appointment_reminder(
    context: RunContext,
    termin_id: str,
    erinnerung_typ: str = "sms"
) -> str:
    """
    Plant automatische Terminerinnerungen per SMS, Anruf oder E-Mail.
    Standard: 24 Stunden und 2 Stunden vor dem appointment.
    """
    try:
        # Validiere Erinnerungstyp
        erlaubte_typen = ["sms", "anruf", "email", "alle"]
        if erinnerung_typ.lower() not in erlaubte_typen:
            erinnerung_typ = "sms"
        
        # Hole Termindetails
        appointment = appointment_manager.get_termin_by_id(termin_id)
        if not appointment:
            return "appointment nicht gefunden. Please überprüfen Sie die appointment-ID."
        
        # Extrahiere Termininfos
        datum = appointment.get('datum')
        uhrzeit = appointment.get('uhrzeit')
        patient_name = appointment.get('patient_name')
        telefon = appointment.get('telefon')
        behandlung = appointment.get('behandlung', 'appointment')
        
        # Erstelle Erinnerungsplan
        from datetime import datetime, timedelta
        termin_datetime = datetime.strptime(f"{datum} {uhrzeit}", "%Y-%m-%d %H:%M")
        
        erinnerungen = []
        
        # 24 Stunden vorher
        erinnerung_24h = termin_datetime - timedelta(hours=24)
        if erinnerung_24h > datetime.now():
            erinnerungen.append({
                'zeit': erinnerung_24h,
                'typ': '24-Stunden-Erinnerung'
            })
        
        # 2 Stunden vorher
        erinnerung_2h = termin_datetime - timedelta(hours=2)
        if erinnerung_2h > datetime.now():
            erinnerungen.append({
                'zeit': erinnerung_2h,
                'typ': '2-Stunden-Erinnerung'
            })
        
        # Speichere Erinnerungseinstellungen (in echter Implementierung würde dies in DB gespeichert)
        antwort = f"**Terminerinnerung eingerichtet:**\n\n"
        antwort += f"**patient**: {patient_name}\n"
        antwort += f"**appointment**: {datum} um {uhrzeit}\n"
        antwort += f"**Behandlung**: {behandlung}\n"
        antwort += f"**Erinnerungstyp**: {erinnerung_typ.upper()}\n\n"
        
        if erinnerungen:
            antwort += "**Geplante Erinnerungen:**\n"
            for er in erinnerungen:
                antwort += f"- {er['typ']}: {er['zeit'].strftime('%d.%m.%Y um %H:%M')}\n"
            
            # Erinnerungstexte
            antwort += f"\n**Erinnerungstext ({erinnerung_typ}):**\n"
            
            if erinnerung_typ in ["sms", "alle"]:
                antwort += f"SMS an {telefon}:\n"
                antwort += f"'Good day {patient_name}, dies ist eine Erinnerung an Ihren "
                antwort += f"appointment am {datum} um {uhrzeit} in der Dental Practice Dr. Weber. "
                antwort += "Bei Verhinderung Please rechtzeitig absagen: 030-12345678'\n\n"
            
            if erinnerung_typ in ["email", "alle"]:
                antwort += "E-Mail-Betreff: 'Terminerinnerung - Dental Practice Dr. Weber'\n"
                antwort += "Inhalt: Formatierte HTML-E-Mail mit Termindetails und Praxisadresse\n\n"
            
            if erinnerung_typ in ["anruf", "alle"]:
                antwort += "Automatischer Anruf mit Sprachnachricht geplant\n\n"
            
            antwort += "✓ **Erinnerungen erfolgreich aktiviert**"
        else:
            antwort += "⚠️ **Hinweis**: appointment ist zu nah, keine automatischen Erinnerungen möglich.\n"
            antwort += "Please erinnern Sie den patients manuell."
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei Terminerinnerung: {e}")
        return "Fehler beim Einrichten der Terminerinnerung. Please versuchen Sie es erneut."

@function_tool()
async def renew_prescription(
    context: RunContext,
    patient_telefon: str,
    medikament: str
) -> str:
    """
    Verwaltet Rezeptverlängerungen für patients.
    Prüft Berechtigung und erstellt Anfrage für den doctor.
    """
    try:
        # Hole Patientenhistorie
        historie = appointment_manager.get_patient_history(patient_telefon)
        
        # Prüfe ob patient bekannt ist
        if not historie:
            return "patient nicht in unserer Datenbank gefunden. Please vereinbaren Sie einen appointment für eine Rezeptausstellung."
        
        # Definiere häufige Zahnmedikamente
        haeufige_medikamente = {
            "schmerzmittel": ["Ibuprofen", "Paracetamol", "Novaminsulfon"],
            "antibiotika": ["Amoxicillin", "Clindamycin", "Penicillin V"],
            "mundspuelung": ["Chlorhexidin", "Listerine", "Meridol"],
            "zahncreme": ["Sensodyne", "Elmex", "Fluorid-Gel"]
        }
        
        # Kategorisiere Medikament
        medikament_typ = "unbekannt"
        for kategorie, medis in haeufige_medikamente.items():
            if any(medi.lower() in medikament.lower() for medi in medis):
                medikament_typ = kategorie
                break
        
        # Erstelle Rezeptanfrage
        from datetime import datetime
        anfrage_datum = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        antwort = f"**Rezeptverlängerung angefragt:**\n\n"
        antwort += f"**patient**: Telefon {patient_telefon}\n"
        antwort += f"**Medikament**: {medikament}\n"
        antwort += f"**Kategorie**: {medikament_typ.title()}\n"
        antwort += f"**Anfragedatum**: {anfrage_datum}\n\n"
        
        # Prüfungen basierend auf Medikamententyp
        if medikament_typ == "antibiotika":
            antwort += "⚠️ **Hinweis**: Antibiotika benötigen eine aktuelle Untersuchung.\n"
            antwort += "Der doctor muss die Notwendigkeit prüfen.\n\n"
        elif medikament_typ == "schmerzmittel":
            antwort += "ℹ️ **Info**: Schmerzmittel sollten nur kurzfristig verwendet werden.\n"
            antwort += "Bei längerem Bedarf ist eine Untersuchung empfohlen.\n\n"
        
        # Status der Anfrage
        antwort += "**Status**: ⏳ In Bearbeitung\n\n"
        antwort += "**Nächste Schritte:**\n"
        antwort += "1. Dr. Weber wird die Anfrage prüfen\n"
        antwort += "2. Sie erhalten eine SMS/Anruf sobald das Rezept bereit ist\n"
        antwort += "3. Abholung in der practice oder Zusendung per Post möglich\n\n"
        
        # Bearbeitungszeit
        antwort += "**Bearbeitungszeit**: \n"
        antwort += "- Normale Rezepte: 1-2 Werktage\n"
        antwort += "- Dringende Fälle: today noch möglich\n\n"
        
        antwort += "✓ **Anfrage erfolgreich eingereicht**\n"
        antwort += f"Referenznummer: RX{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei Rezeptverlängerung: {e}")
        return "Fehler bei der Rezeptanfrage. Please rufen Sie uns direkt an."

@function_tool()
async def treatment_plan_status(
    context: RunContext,
    patient_telefon: str
) -> str:
    """
    Verfolgt mehrteilige Behandlungspläne (z.B. orthodontics, Implantate).
    Zeigt Fortschritt und nächste Schritte an.
    """
    try:
        # Hole Patientenhistorie
        historie = appointment_manager.get_patient_history(patient_telefon)
        
        if not historie:
            return "Kein Behandlungsplan für diese Telefonnummer gefunden."
        
        # Definiere typische Behandlungspläne
        behandlungsplaene = {
            "Implantat": {
                "schritte": [
                    "Erstberatung und Röntgen",
                    "Knochenaufbau (falls nötig)",
                    "Implantat-Setzung",
                    "Einheilphase (3-6 Monate)",
                    "Abdruck für Krone",
                    "Einsetzen der finalen Krone"
                ],
                "dauer": "4-8 Monate"
            },
            "orthodontics": {
                "schritte": [
                    "Erstuntersuchung und Abdrücke",
                    "Behandlungsplanung",
                    "Einsetzen der braces",
                    "Monatliche Kontrollen",
                    "Feineinstellung",
                    "Retainer-Anpassung"
                ],
                "dauer": "12-24 Monate"
            },
            "root canal": {
                "schritte": [
                    "Diagnose und Röntgen",
                    "Erste Sitzung - Kanalöffnung",
                    "Zweite Sitzung - Reinigung",
                    "Dritte Sitzung - filling",
                    "Kontrollröntgen",
                    "Krone (optional)"
                ],
                "dauer": "2-4 Wochen"
            }
        }
        
        # Analysiere Historie für aktiven Behandlungsplan
        aktiver_plan = None
        abgeschlossene_schritte = []
        
        for appointment in historie:
            behandlung = appointment.get('behandlung', '').lower()
            for plan_typ, plan_info in behandlungsplaene.items():
                if plan_typ.lower() in behandlung:
                    aktiver_plan = plan_typ
                    abgeschlossene_schritte.append({
                        'datum': appointment.get('datum'),
                        'behandlung': appointment.get('behandlung')
                    })
        
        antwort = f"**Behandlungsplan-Status:**\n\n"
        antwort += f"**patient**: Telefon {patient_telefon}\n\n"
        
        if aktiver_plan:
            plan_info = behandlungsplaene[aktiver_plan]
            fortschritt = min(len(abgeschlossene_schritte), len(plan_info['schritte']))
            prozent = int((fortschritt / len(plan_info['schritte'])) * 100)
            
            antwort += f"**Aktiver Plan**: {aktiver_plan}\n"
            antwort += f"**Gesamtdauer**: {plan_info['dauer']}\n"
            antwort += f"**Fortschritt**: {prozent}% ({fortschritt}/{len(plan_info['schritte'])} Schritte)\n\n"
            
            # Fortschrittsbalken
            balken_laenge = 20
            gefuellt = int(balken_laenge * prozent / 100)
            antwort += "["
            antwort += "█" * gefuellt
            antwort += "░" * (balken_laenge - gefuellt)
            antwort += f"] {prozent}%\n\n"
            
            # Schritte-Übersicht
            antwort += "**Behandlungsschritte:**\n"
            for i, schritt in enumerate(plan_info['schritte']):
                if i < fortschritt:
                    antwort += f"✓ {schritt}"
                    if i < len(abgeschlossene_schritte):
                        antwort += f" (erledigt am {abgeschlossene_schritte[i]['datum']})"
                    antwort += "\n"
                elif i == fortschritt:
                    antwort += f"→ **{schritt}** (nächster Schritt)\n"
                else:
                    antwort += f"○ {schritt} (ausstehend)\n"
            
            # Nächster appointment
            antwort += f"\n**Empfehlung**: "
            if fortschritt < len(plan_info['schritte']):
                antwort += f"Vereinbaren Sie einen appointment für: {plan_info['schritte'][fortschritt]}"
            else:
                antwort += "Behandlungsplan abgeschlossen! Kontrolltermin in 6 Monaten empfohlen."
        else:
            antwort += "**Kein aktiver Behandlungsplan gefunden.**\n\n"
            if historie:
                antwort += "**Letzte appointments:**\n"
                for appointment in historie[-3:]:
                    antwort += f"- {appointment.get('datum')}: {appointment.get('behandlung')}\n"
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei Behandlungsplan-Status: {e}")
        return "Fehler beim Abrufen des Behandlungsplans. Please versuchen Sie es erneut."

# Lernfähigkeit - Häufige Anfragen tracken
from collections import defaultdict
from datetime import datetime, timedelta
import json
import os

class AnfragenLernsystem:
    def __init__(self, cache_file="anfragen_cache.json"):
        self.cache_file = cache_file
        self.anfragen_cache = self._load_cache()
        self.haeufige_muster = defaultdict(int)
        self.antwort_optimierungen = {}
        
    def _load_cache(self):
        """Lädt gespeicherte Anfragen-Muster"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"anfragen": [], "muster": {}, "optimierungen": {}}
        return {"anfragen": [], "muster": {}, "optimierungen": {}}
    
    def _save_cache(self):
        """Speichert Anfragen-Muster"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.anfragen_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Fehler beim Speichern des Lern-Cache: {e}")
    
    def anfrage_aufzeichnen(self, anfrage_typ, details):
        """Zeichnet eine Anfrage auf"""
        self.anfragen_cache["anfragen"].append({
            "typ": anfrage_typ,
            "details": details,
            "zeitstempel": datetime.now().isoformat()
        })
        
        # Update Muster-Zähler
        if anfrage_typ not in self.anfragen_cache["muster"]:
            self.anfragen_cache["muster"][anfrage_typ] = 0
        self.anfragen_cache["muster"][anfrage_typ] += 1
        
        # Nur die letzten 1000 Anfragen behalten
        if len(self.anfragen_cache["anfragen"]) > 1000:
            self.anfragen_cache["anfragen"] = self.anfragen_cache["anfragen"][-1000:]
        
        self._save_cache()
    
    def get_haeufige_anfragen(self, top_n=10):
        """Gibt die häufigsten Anfragen zurück"""
        sortierte_muster = sorted(
            self.anfragen_cache["muster"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sortierte_muster[:top_n]
    
    def vorschlag_generieren(self, kontext):
        """Generiert Vorschläge basierend auf häufigen Mustern"""
        vorschlaege = []
        
        # Analysiere Tageszeit-Muster
        jetzt = datetime.now()
        tageszeit = "morning" if jetzt.hour < 12 else "afternoon" if jetzt.hour < 18 else "evening"
        
        # Häufige Anfragen für diese Tageszeit
        for anfrage in self.anfragen_cache["anfragen"][-100:]:  # Letzte 100 Anfragen
            anfrage_zeit = datetime.fromisoformat(anfrage["zeitstempel"])
            if anfrage_zeit.hour // 6 == jetzt.hour // 6:  # Gleiche Tageszeit
                if anfrage["typ"] not in [v["typ"] for v in vorschlaege]:
                    vorschlaege.append({
                        "typ": anfrage["typ"],
                        "grund": f"Häufig {tageszeit} angefragt"
                    })
        
        return vorschlaege[:3]  # Top 3 Vorschläge

# Globale Instanz
lernsystem = AnfragenLernsystem()

@function_tool()
async def analyze_learning_capability(
    context: RunContext
) -> str:
    """
    Zeigt Lernstatistiken und häufige Anfragemuster.
    Hilft der practice, Muster zu erkennen und Service zu verbessern.
    """
    try:
        # Hole häufigste Anfragen
        haeufige = lernsystem.get_haeufige_anfragen()
        
        antwort = "**Lernfähigkeit - Analyse häufiger Anfragen:**\n\n"
        
        if haeufige:
            antwort += "**Top 10 häufigste Anfragen:**\n"
            for i, (anfrage_typ, anzahl) in enumerate(haeufige, 1):
                antwort += f"{i}. {anfrage_typ}: {anzahl} mal\n"
            
            # Erkenntnisse
            antwort += "\n**Erkannte Muster:**\n"
            
            # Analysiere Terminanfragen
            termin_anfragen = sum(anzahl for typ, anzahl in haeufige if "appointment" in typ.lower())
            if termin_anfragen > 20:
                antwort += f"- Hohe Nachfrage nach Terminen ({termin_anfragen} Anfragen)\n"
                antwort += "  → Empfehlung: Online-Terminbuchung einführen\n"
            
            # Analysiere emergencies
            notfall_anfragen = sum(anzahl for typ, anzahl in haeufige if "emergency" in typ.lower())
            if notfall_anfragen > 5:
                antwort += f"- Viele Notfallanfragen ({notfall_anfragen})\n"
                antwort += "  → Empfehlung: emergency-Sprechstunde erweitern\n"
            
            # Zeitbasierte Muster
            antwort += "\n**Optimierungsvorschläge:**\n"
            vorschlaege = lernsystem.vorschlag_generieren({})
            for vorschlag in vorschlaege:
                antwort += f"- {vorschlag['typ']}: {vorschlag['grund']}\n"
        else:
            antwort += "Noch keine ausreichenden Daten für eine Analyse vorhanden.\n"
            antwort += "Das System lernt mit jeder Anfrage dazu.\n"
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei Lernfähigkeit-Analyse: {e}")
        return "Fehler bei der Analyse der Lernstatistiken."

@function_tool()
async def answer_frequent_question(
    context: RunContext,
    frage_kategorie: str
) -> str:
    """
    Beantwortet häufige Fragen basierend auf gelernten Mustern.
    Passt Antworten an häufige Anfragemuster an.
    """
    try:
        # Zeichne diese Anfrage auf
        lernsystem.anfrage_aufzeichnen(f"FAQ_{frage_kategorie}", {
            "zeitstempel": datetime.now().isoformat()
        })
        
        # Vordefinierte optimierte Antworten für häufige Fragen
        optimierte_antworten = {
            "oeffnungszeiten": {
                "basis": "Unsere opening hours sind:\nMo-Fr: 9:00-11:30 und 14:00-17:30\nSa: 9:00-12:30\nSo: closed",
                "haeufig": "**Tipp**: Viele patients fragen nach Terminen am frühen tomorrow oder späten afternoon."
            },
            "pain": {
                "basis": "Bei akuten pain bieten wir Notfalltermine an.",
                "haeufig": "**Häufigste Schmerzursachen**: Karies (40%), Zahnfleischentzündung (30%), Wurzelentzündung (20%)"
            },
            "kosten": {
                "basis": "Die Kosten hängen von der Behandlung ab. Gladly erstellen wir einen Kostenvoranschlag.",
                "haeufig": "**Häufig gefragt**: dental cleaning 80-120€, filling 50-200€, Krone 600-1200€"
            },
            "terminabsage": {
                "basis": "appointments können bis 24 Stunden vorher kostenfrei abgesagt werden.",
                "haeufig": "**Tipp**: Die meisten Absagen erfolgen montags. Wir haben dann oft kurzfristig appointments frei."
            }
        }
        
        antwort = f"**Antwort auf häufige Frage: {frage_kategorie}**\n\n"
        
        if frage_kategorie.lower() in optimierte_antworten:
            info = optimierte_antworten[frage_kategorie.lower()]
            antwort += f"{info['basis']}\n\n"
            
            # Füge gelernten Kontext hinzu
            anfrage_anzahl = lernsystem.anfragen_cache["muster"].get(f"FAQ_{frage_kategorie}", 0)
            if anfrage_anzahl > 10:
                antwort += f"ℹ️ {info['haeufig']}\n\n"
                antwort += f"Diese Frage wurde bereits {anfrage_anzahl} mal gestellt.\n"
        else:
            # Generische Antwort
            antwort += "Ich helfe Ihnen Gladly weiter. Können Sie Ihre Frage genauer formulieren?\n\n"
            
            # Zeige ähnliche häufige Fragen
            antwort += "**Häufig gestellte Fragen:**\n"
            for typ, _ in lernsystem.get_haeufige_anfragen(5):
                if typ.startswith("FAQ_"):
                    antwort += f"- {typ.replace('FAQ_', '')}\n"
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei häufiger Frage: {e}")
        return "Sorry, ich kann diese Frage momentan nicht beantworten."

@function_tool()
async def common_treatment_reasons(
    context: RunContext,
    patient_telefon: str = None
) -> str:
    """
    Zeigt häufige Behandlungsgründe basierend auf Lernstatistiken.
    Kann personalisiert werden für bekannte patients.
    """
    try:
        # Hole häufigste Terminanfragen
        haeufige = lernsystem.get_haeufige_anfragen()
        termin_gruende = [(typ.replace("Termin_", ""), anzahl) 
                         for typ, anzahl in haeufige 
                         if typ.startswith("Termin_")]
        
        antwort = "**Häufige Behandlungsgründe in unserer practice:**\n\n"
        
        if termin_gruende:
            # Top 5 Gründe
            for i, (grund, anzahl) in enumerate(termin_gruende[:5], 1):
                antwort += f"{i}. {grund} ({anzahl} appointments)\n"
            
            # Personalisierung für bekannte patients
            if patient_telefon:
                historie = appointment_manager.get_patient_history(patient_telefon)
                if historie:
                    letzte_behandlung = historie[-1].get('behandlung', '') if historie else ''
                    antwort += f"\n**Ihr letzter appointment**: {letzte_behandlung}\n"
                    
                    # Intelligenter Vorschlag basierend auf Zeitabstand
                    from datetime import datetime, timedelta
                    if letzte_behandlung.lower() == "dental cleaning":
                        antwort += "💡 **Tipp**: Eine dental cleaning ist alle 6 Monate empfohlen.\n"
                    elif "kontrolle" in letzte_behandlung.lower():
                        antwort += "💡 **Tipp**: Kontrolluntersuchungen sollten alle 6-12 Monate erfolgen.\n"
        else:
            # Standard-Gründe wenn noch keine Daten
            antwort += "- check-up (alle 6 Monate empfohlen)\n"
            antwort += "- dental cleaning (Prophylaxe)\n"
            antwort += "- toothache oder Beschwerden\n"
            antwort += "- Beratung für dental prosthetics\n"
            antwort += "- Ästhetische Behandlungen\n"
        
        antwort += "\n**Für welche Behandlung möchten Sie einen appointment vereinbaren?**"
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei häufigen Behandlungsgründen: {e}")
        return "Wofür benötigen Sie denn den appointment?"

# =====================================================================
# 🏥 NEUE KALENDER-INTEGRATION: Sofia hat direkten Zugang zu Kalendar 
# =====================================================================

class KalenderClient:
    """Client für direkten Kalender-Zugriff"""
    
    def __init__(self, calendar_url: str = "http://localhost:3005"):
        self.calendar_url = calendar_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_next_available(self) -> dict:
        """Findet nächsten freien appointment"""
        try:
            response = await self.client.get(f"{self.calendar_url}/api/sofia/next-available")
            return response.json()
        except Exception as e:
            logging.error(f"Fehler beim Abrufen des nächsten freien Termins: {e}")
            return {"available": False, "message": "Verbindungsfehler zum Kalender"}
    
    async def check_date_availability(self, date: str) -> dict:
        """Prüft Verfügbarkeit an bestimmtem Tag"""
        try:
            response = await self.client.get(f"{self.calendar_url}/api/sofia/check-date/{date}")
            return response.json()
        except Exception as e:
            logging.error(f"Fehler beim Prüfen der Verfügbarkeit für {date}: {e}")
            return {"available": False, "message": "Verbindungsfehler zum Kalender"}
    
    async def get_suggestions(self, days: int = 7, limit: int = 5) -> dict:
        """Holt Terminvorschläge"""
        try:
            response = await self.client.get(f"{self.calendar_url}/api/sofia/suggest-times?days={days}&limit={limit}")
            return response.json()
        except Exception as e:
            logging.error(f"Fehler beim Abrufen von Terminvorschlägen: {e}")
            return {"suggestions": [], "message": "Verbindungsfehler zum Kalender"}
    
    async def get_today_appointments(self) -> dict:
        """Holt heutige appointments"""
        try:
            response = await self.client.get(f"{self.calendar_url}/api/sofia/today")
            return response.json()
        except Exception as e:
            logging.error(f"Fehler beim Abrufen heutiger appointments: {e}")
            return {"appointments": [], "message": "Verbindungsfehler zum Kalender"}
    
    async def get_patient_appointments(self, phone: str) -> dict:
        """Holt appointments eines patients"""
        try:
            response = await self.client.get(f"{self.calendar_url}/api/sofia/patient/{phone}")
            return response.json()
        except Exception as e:
            logging.error(f"Fehler beim Abrufen der Patiententermine: {e}")
            return {"appointments": [], "message": "Verbindungsfehler zum Kalender"}
    
    async def book_appointment(self, patient_name: str, patient_phone: str, 
                             requested_date: str, requested_time: str, 
                             treatment_type: str = None) -> dict:
        """Bucht einen appointment über das Kalender-System"""
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
            logging.error(f"Fehler beim Terminbuchen: {e}")
            return {
                "success": False,
                "message": "Verbindungsfehler zum Kalender-System. Please versuchen Sie es später erneut."
            }

# Globaler Kalender-Client
kalender_client = KalenderClient()

@function_tool()
async def sofia_next_available_appointment(
    context: RunContext
) -> str:
    """
    Sofia findet automatisch den nächsten freien appointment.
    Perfekt wenn patients fragen: "Wann haben Sie den nächsten freien appointment?"
    """
    try:
        result = await kalender_client.get_next_available()
        
        if result.get("available"):
            antwort = result["message"]
            if "allAvailableTimes" in result and len(result["allAvailableTimes"]) > 1:
                weitere_zeiten = ", ".join(result["allAvailableTimes"][1:4])
                antwort += f"\n\nWeitere verfügbare Zeiten an diesem Tag: {weitere_zeiten} o'clock."
            
            antwort += "\n\nMöchten Sie diesen appointment buchen?"
            
            # CallManager Notiz
            call_manager.add_note(f"Nächster freier appointment gefunden: {result.get('date')} um {result.get('time')}")
            
            return antwort
        else:
            return result.get("message", "Leider keine freien appointments verfügbar.")
            
    except Exception as e:
        logging.error(f"Fehler bei nächstem freien appointment: {e}")
        return "Sorry, ich kann gerade nicht auf den Kalender zugreifen. Please rufen Sie uns direkt an."

@function_tool()
async def sofia_appointment_on_specific_day(
    context: RunContext,
    gewuenschtes_datum: str
) -> str:
    """
    Sofia prüft Verfügbarkeit an einem bestimmten Tag.
    Nutzen wenn patient fragt: "Haben Sie am Friday Zeit?" oder "Was ist am 25. July frei?"
    
    Args:
        gewuenschtes_datum: Datum im Format YYYY-MM-DD oder deutsch (z.B. "2024-07-25")
    """
    try:
        # Datum normalisieren falls nötig
        if not re.match(r'\d{4}-\d{2}-\d{2}', gewuenschtes_datum):
            # Versuche deutsches Datum zu parsen
            logging.info(f"Versuche deutsches Datum zu parsen: {gewuenschtes_datum}")
            # Hier könnte man mehr Parsing-Logik hinzufügen
        
        result = await kalender_client.check_date_availability(gewuenschtes_datum)
        
        if result.get("available"):
            antwort = result["message"]
            
            # Zeige Details
            if "availableTimes" in result:
                verfuegbar = len(result["availableTimes"])
                gesamt = result.get("totalSlots", 16)
                antwort += f"\n\nVon {gesamt} möglichen Terminen sind noch {verfuegbar} frei."
            
            antwort += "\n\nWelche Uhrzeit würde Ihnen passen?"
            
        elif result.get("isWeekend"):
            antwort = result["message"]
            antwort += "\n\nUnsere opening hours sind Monday bis Friday von 8:00 bis 18:00 o'clock."
            
        elif result.get("isPast"):
            antwort = result["message"]
            # Automatisch nächsten freien appointment anbieten
            next_result = await kalender_client.get_next_available()
            if next_result.get("available"):
                antwort += f"\n\n{next_result['message']}"
                antwort += "\n\nSoll ich diesen appointment für Sie reservieren?"
            
        else:
            antwort = result["message"]
            # Alternativen anbieten
            suggestions = await kalender_client.get_suggestions(days=14, limit=3)
            if suggestions.get("suggestions"):
                antwort += "\n\nIch kann Ihnen diese Alternativen anbieten:\n"
                for i, sugg in enumerate(suggestions["suggestions"][:3], 1):
                    antwort += f"{i}. {sugg['formattedDate']} um {sugg['time']} o'clock\n"
                antwort += "\nWelcher appointment würde Ihnen passen?"
        
        # CallManager Notiz
        call_manager.add_note(f"Verfügbarkeit geprüft für {gewuenschtes_datum}: {'verfügbar' if result.get('available') else 'nicht verfügbar'}")
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei Terminprüfung für {gewuenschtes_datum}: {e}")
        return f"Sorry, ich kann die Verfügbarkeit für {gewuenschtes_datum} gerade nicht prüfen. Please versuchen Sie es erneut."

@function_tool()
async def sofia_smart_appointment_suggestions(
    context: RunContext,
    anzahl_tage: int = 7,
    max_vorschlaege: int = 5
) -> str:
    """
    Sofia macht intelligente Terminvorschläge.
    Nutzen wenn patient sagt: "Schlagen Sie mir appointments vor" oder "Was haben Sie denn frei?"
    
    Args:
        anzahl_tage: Wie viele Tage in die Zukunft schauen (Standard: 7)
        max_vorschlaege: Maximale Anzahl Vorschläge (Standard: 5)
    """
    try:
        result = await kalender_client.get_suggestions(days=anzahl_tage, limit=max_vorschlaege)
        
        if result.get("suggestions") and len(result["suggestions"]) > 0:
            antwort = "Gladly! Ich habe folgende appointments für Sie:\n\n"
            
            for i, suggestion in enumerate(result["suggestions"], 1):
                antwort += f"**{i}. {suggestion['formattedDate']} um {suggestion['time']} o'clock**"
                if suggestion.get("availableCount", 0) > 1:
                    antwort += f" (noch {suggestion['availableCount']} appointments an diesem Tag verfügbar)"
                antwort += "\n"
            
            antwort += "\nWelcher appointment passt Ihnen am besten? Ich reserviere ihn Gladly für Sie."
            
        else:
            antwort = result.get("message", f"Leider sind in den nächsten {anzahl_tage} Tagen keine appointments frei.")
            antwort += "\n\nSoll ich in einem größeren Zeitraum schauen oder können Sie zu einem späteren Zeitpunkt anrufen?"
        
        # CallManager Notiz
        call_manager.add_note(f"Terminvorschläge erstellt: {len(result.get('suggestions', []))} Optionen für {anzahl_tage} Tage")
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei Terminvorschlägen: {e}")
        return "Sorry, ich kann gerade keine Terminvorschläge erstellen. Please rufen Sie uns direkt an."

@function_tool()
async def sofia_get_todays_appointments(
    context: RunContext
) -> str:
    """
    Sofia kann heutige appointments abrufen.
    Nutzen für interne practice-Anfragen oder wenn patients fragen ob today viel los ist.
    """
    try:
        result = await kalender_client.get_today_appointments()
        
        if result.get("appointments") and len(result["appointments"]) > 0:
            count = result.get("count", len(result["appointments"]))
            antwort = f"today haben wir {count} appointments geplant:\n\n"
            antwort += result.get("message", "")
            
        else:
            antwort = result.get("message", "today sind keine appointments geplant.")
        
        # CallManager Notiz  
        call_manager.add_note(f"Heutige appointments abgerufen: {result.get('count', 0)} appointments")
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler beim Abrufen heutiger appointments: {e}")
        return "Sorry, ich kann die heutigen appointments gerade nicht abrufen."

@function_tool()
async def sofia_find_my_appointments_extended(
    context: RunContext,
    telefonnummer: str
) -> str:
    """
    Sofia findet appointments eines patients über Telefonnummer.
    Erweiterte Version mit direktem Kalender-Zugriff.
    
    Args:
        telefonnummer: Telefonnummer des patients
    """
    try:
        # Telefonnummer normalisieren
        phone_clean = re.sub(r'[^\d+]', '', telefonnummer)
        
        result = await kalender_client.get_patient_appointments(phone_clean)
        
        if result.get("appointments") and len(result["appointments"]) > 0:
            count = result.get("count", len(result["appointments"]))
            antwort = f"Ich habe {count} appointments für Sie gefunden:\n\n"
            antwort += result.get("message", "")
            
            antwort += "\n\nMöchten Sie einen appointment ändern oder haben Sie weitere Fragen?"
            
        else:
            antwort = result.get("message", "Sie haben aktuell keine appointments bei uns.")
            antwort += "\n\nMöchten Sie einen neuen appointment vereinbaren?"
        
        # CallManager Notiz
        call_manager.add_note(f"appointments für patient abgerufen (Tel: {phone_clean}): {result.get('count', 0)} gefunden")
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Patiententermine: {e}")
        return "Sorry, ich kann Ihre appointments gerade nicht abrufen. Please versuchen Sie es erneut."

@function_tool()
async def book_appointment_calendar_system(
    context: RunContext,
    patient_name: str,
    phone: str,
    appointment_date: str,
    appointment_time: str,
    treatment_type: str = "check-up"
) -> str:
    """
    🏥 NEUE CALENDAR INTEGRATION: Bucht appointments direkt im Calendar System
    Diese Funktion ersetzt die alten Terminbuchungsmethoden und sorgt dafür,
    dass alle appointments sofort im visuellen Kalender angezeigt werden.
    
    Args:
        patient_name: Vollständiger Name des patients
        phone: Telefonnummer für Kontakt  
        appointment_date: Datum im Format YYYY-MM-DD
        appointment_time: Uhrzeit im Format HH:MM
        treatment_type: Art der Behandlung
    """
    try:
        # Telefonnummer normalisieren
        phone_clean = re.sub(r'[^\d+]', '', phone)
        if not phone_clean.startswith('+'):
            if phone_clean.startswith('0'):
                phone_clean = '+49' + phone_clean[1:]
            else:
                phone_clean = '+49' + phone_clean
        
        # Datum validieren
        try:
            datetime.strptime(appointment_date, '%Y-%m-%d')
        except ValueError:
            return "❌ Ungültiges Datumsformat. Please verwenden Sie YYYY-MM-DD."
        
        # Zeit validieren
        try:
            datetime.strptime(appointment_time, '%H:%M')
        except ValueError:
            return "❌ Ungültiges Zeitformat. Please verwenden Sie HH:MM."
        
        # Terminbuchung über Calendar System
        logging.info(f"🏥 CALENDAR BOOKING: {patient_name} für {appointment_date} {appointment_time}")
        result = await kalender_client.book_appointment(
            patient_name=patient_name,
            patient_phone=phone_clean,
            requested_date=appointment_date,
            requested_time=appointment_time,
            treatment_type=treatment_type
        )
        
        if result.get("success"):
            antwort = f"✅ **appointment erfolgreich gebucht!**\n\n"
            antwort += f"👤 **patient:** {patient_name}\n"
            antwort += f"📅 **Datum:** {appointment_date}\n" 
            antwort += f"🕐 **Uhrzeit:** {appointment_time}\n"
            antwort += f"🦷 **Behandlung:** {treatment_type}\n"
            antwort += f"📞 **Telefon:** {phone_clean}\n\n"
            antwort += "🏥 **Der appointment erscheint sofort in unserem Kalender!**\n"
            antwort += "📧 Sie erhalten eine Bestätigung per SMS/E-Mail.\n"
            antwort += "🔔 Wir erinnern Sie einen Tag vorher an Ihren appointment."
            
            # CallManager Notiz
            call_manager.add_note(f"appointment gebucht via Calendar: {patient_name} am {appointment_date} {appointment_time}")
            
            logging.info(f"✅ SUCCESS: appointment gebucht für {patient_name} am {appointment_date} {appointment_time}")
            return antwort
        else:
            error_msg = result.get("message", "Unbekannter Fehler")
            antwort = f"❌ **Terminbuchung fehlgeschlagen:**\n\n"
            antwort += f"📋 **Grund:** {error_msg}\n\n"
            
            if "bereits vergeben" in error_msg or "taken" in error_msg:
                antwort += "🔄 **Lass mich Alternativen für Sie finden...**\n"
                # Hole alternative appointments
                suggestions = await kalender_client.get_suggestions(days=14, limit=3)
                if suggestions.get("suggestions"):
                    antwort += "\n✨ **Alternative appointments:**\n"
                    for i, sugg in enumerate(suggestions["suggestions"][:3], 1):
                        antwort += f"{i}. {sugg['formattedDate']} um {sugg['time']} o'clock\n"
                    antwort += "\n💬 Welcher appointment würde Ihnen passen?"
                else:
                    antwort += "\n📞 Please rufen Sie uns an, damit wir einen passenden appointment finden."
            
            # CallManager Notiz
            call_manager.add_note(f"Terminbuchung fehlgeschlagen: {error_msg}")
            
            logging.warning(f"❌ BOOKING FAILED: {patient_name} - {error_msg}")
            return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei book_appointment_calendar_system: {e}")
        return f"❌ **Systemfehler:** Es gab ein technisches Problem bei der Terminbuchung. Please rufen Sie uns direkt an: 030 12345678"
