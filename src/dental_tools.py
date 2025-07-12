import logging
import re
from functools import lru_cache
from livekit.agents import function_tool, RunContext
from datetime import datetime, timedelta, timedelta
from typing import Optional, Dict, List
from enum import Enum
import json
import locale
# 🚀 PERFORMANCE BOOST: Fuzzy Times für unscharfe Zeitangaben
FUZZY_TIMES = {
    "kurz nach 14": "14:15",
    "kurz nach 2": "14:15",
    "gegen halb 3": "14:30",
    "gegen halb 15": "14:30",
    "später nachmittag": "16:00",
    "früher nachmittag": "13:00",
    "früh morgens": "08:00",
    "spät abends": "19:00",
    "mittags": "12:00",
    "gegen mittag": "12:00",
    "am vormittag": "10:00",
    "vormittags": "10:00",
    "nachmittags": "15:00",
    "am nachmittag": "15:00",
    "gegen 14": "14:00",
    "gegen 15": "15:00",
    "gegen 16": "16:00",
    "gegen 17": "17:00",
    "kurz vor 15": "14:45",
    "kurz vor 16": "15:45",
    "kurz vor 17": "16:45",
    "nach dem mittagessen": "13:30",
    "vor dem mittagessen": "11:30",
    "nach feierabend": "18:00",
    "in der mittagspause": "12:30"
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
            r'(\d{1,2}) uhr',       # 11 uhr
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
    'name': 'Zahnarztpraxis Dr. Weber',
    'address': 'Musterstraße 123, 12345 Berlin',
    'phone': '030 12345678',
    'email': 'info@zahnarzt-weber.de',
    'website': 'www.zahnarzt-weber.de',
    'opening_hours': {
        'monday': '08:00-18:00',
        'tuesday': '08:00-18:00',
        'wednesday': '08:00-18:00',
        'thursday': '08:00-18:00',
        'friday': '08:00-16:00',
        'saturday': 'Geschlossen',
        'sunday': 'Geschlossen'
    }
}

SERVICES = [
    'Kontrolluntersuchung',
    'Zahnreinigung',
    'Füllungen',
    'Wurzelbehandlung',
    'Zahnersatz',
    'Implantate',
    'Kieferorthopädie',
    'Notfallbehandlung'
]

FAQ = {
    'Kosten': 'Die Kosten variieren je nach Behandlung. Kontaktieren Sie uns für ein Angebot.',
    'Termine': 'Termine können telefonisch oder online gebucht werden.',
    'Notfall': 'Bei Notfällen rufen Sie bitte sofort an.'
}

APPOINTMENT_TYPES = {
    'Kontrolluntersuchung': 30,
    'Zahnreinigung': 60,
    'Füllungen': 45,
    'Wurzelbehandlung': 90,
    'Zahnersatz': 60,
    'Implantate': 120,
    'Kieferorthopädie': 45,
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
    0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag',
    4: 'Freitag', 5: 'Samstag', 6: 'Sonntag'
}

GERMAN_MONTHS = {
    1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
    7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
}

def get_current_datetime_info():
    """
    Gibt automatisch das aktuelle Datum und die Uhrzeit zurück.
    ✅ KONSISTENTE datetime-Verwendung - keine String/datetime Mischung
    """
    now = datetime.now()

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
        'is_weekend': now.weekday() >= 5,  # Samstag=5, Sonntag=6
        'tomorrow_weekday': GERMAN_WEEKDAYS[(now.weekday() + 1) % 7]
    }

    # ✅ RELATIVE DATUMS-BERECHNUNGEN hinzufügen
    morgen = now + timedelta(days=1)
    übermorgen = now + timedelta(days=2)

    # Nächste Woche = Montag der nächsten Woche
    tage_bis_naechster_montag = (7 - now.weekday()) % 7
    if tage_bis_naechster_montag == 0:  # Heute ist Montag
        tage_bis_naechster_montag = 7  # Nächster Montag
    naechste_woche = now + timedelta(days=tage_bis_naechster_montag)

    # Kalenderwoche berechnen
    kalenderwoche = now.isocalendar()[1]

    # Erweiterte Informationen hinzufügen
    date_info.update({
        # Relative Daten
        'morgen': f"{GERMAN_WEEKDAYS[morgen.weekday()]}, {morgen.day}. {GERMAN_MONTHS[morgen.month]} {morgen.year}",
        'morgen_iso': morgen.strftime("%Y-%m-%d"),
        'übermorgen': f"{GERMAN_WEEKDAYS[übermorgen.weekday()]}, {übermorgen.day}. {GERMAN_MONTHS[übermorgen.month]} {übermorgen.year}",
        'übermorgen_iso': übermorgen.strftime("%Y-%m-%d"),
        'nächste_woche': f"{GERMAN_WEEKDAYS[naechste_woche.weekday()]}, {naechste_woche.day}. {GERMAN_MONTHS[naechste_woche.month]} {naechste_woche.year}",
        'nächste_woche_iso': naechste_woche.strftime("%Y-%m-%d"),
        'kalenderwoche': kalenderwoche,

        # datetime-Objekte für weitere Berechnungen
        'morgen_datetime': morgen,
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

    # 🦷 SCHMERZEN - Natürliche Nachfragen
    if any(word in symptom_oder_grund for word in ['schmerz', 'schmerzen', 'weh', 'tut weh', 'ziehen', 'stechen', 'pochen']):
        return "Oh, das tut mir leid zu hören, dass Sie Schmerzen haben. Seit wann haben Sie denn die Beschwerden? Und haben Sie schon Schmerzmittel genommen?"

    # 🦷 IMPLANTAT - Natürliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['implantat', 'implant', 'zahnersatz', 'künstlicher zahn']):
        return "Ah, es geht um Ihr Implantat. Ist das nur für eine Kontrolluntersuchung oder haben Sie Probleme damit?"

    # 🦷 ZAHNFLEISCH - Natürliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['zahnfleisch', 'gingiva', 'blut', 'blutet', 'geschwollen', 'entzündet', 'parodont']):
        return "Ich verstehe, Sie haben Probleme mit dem Zahnfleisch. Blutet es beim Zähneputzen oder ist es geschwollen?"

    # 🦷 WEISHEITSZÄHNE - Natürliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['weisheitszahn', 'weisheitszähne', 'achter', '8er']):
        return "Ach so, es geht um die Weisheitszähne. Haben Sie Schmerzen oder möchten Sie sie entfernen lassen?"

    # 🦷 KRONE/FÜLLUNG - Natürliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['krone', 'füllung', 'plombe', 'inlay', 'onlay', 'abgebrochen', 'rausgefallen']):
        return "Oh, ist etwas mit einer Füllung oder Krone passiert? Ist sie abgebrochen oder rausgefallen?"

    # 🦷 KONTROLLE/PROPHYLAXE - Freundliche Nachfragen
    elif any(word in symptom_oder_grund for word in ['kontrolle', 'untersuchung', 'check', 'prophylaxe', 'reinigung', 'vorsorge']):
        return "Das ist sehr gut, dass Sie zur Kontrolle kommen möchten. Wann waren Sie denn das letzte Mal beim Zahnarzt?"

    # 🦷 BLEACHING/ÄSTHETIK - Beratungsansatz
    elif any(word in symptom_oder_grund for word in ['bleaching', 'aufhellen', 'weiß', 'ästhetik', 'schön', 'verfärb']):
        return "Schön, dass Sie sich für ästhetische Zahnbehandlung interessieren. Möchten Sie Ihre Zähne aufhellen lassen?"

    # 🚨 NOTFALL - Sofortige Hilfe
    elif any(word in symptom_oder_grund for word in ['notfall', 'dringend', 'sofort', 'starke schmerzen', 'unerträglich', 'geschwollen']):
        return "Das klingt nach einem Notfall! Haben Sie starke Schmerzen? Ich suche sofort einen dringenden Termin für Sie."

    # 🦷 ALLGEMEINE BEHANDLUNG - Standard-Nachfragen
    else:
        return "Gerne helfe ich Ihnen weiter. Können Sie mir sagen, was für Beschwerden Sie haben oder welche Behandlung Sie benötigen?"

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
            return None, "Der Termin muss in der Zukunft liegen."

        # Prüfe Geschäftszeiten
        weekday = appointment_datetime.weekday()
        hour = appointment_datetime.hour

        # Sonntag = 6
        if weekday == 6:
            return None, "Sonntags sind wir geschlossen."

        # Samstag = 5 (nur vormittags)
        if weekday == 5 and (hour < 9 or hour >= 13):
            return None, "Samstags sind wir nur von 9:00-12:30 geöffnet."

        # Montag-Freitag
        if weekday < 5:
            if hour < 9 or hour >= 18:
                return None, "Unsere Öffnungszeiten sind Mo-Do: 9:00-17:30, Fr: 9:00-16:00."
            if 11 < hour < 14:  # Mittagspause
                return None, "Während der Mittagspause (11:30-14:00) sind keine Termine möglich."

        # Freitag (nur bis 16:00)
        if weekday == 4 and hour >= 16:
            return None, "Freitags sind wir nur bis 16:00 geöffnet."

        return appointment_datetime, None

    except ValueError:
        return None, "Ungültiges Datum- oder Zeitformat. Verwenden Sie YYYY-MM-DD und HH:MM."
from src.appointment_manager import appointment_manager

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
            summary += f"Patient: {self.patient_info.get('name', 'N/A')}\n"
            summary += f"Telefon: {self.patient_info.get('phone', 'N/A')}\n"
        if self.scheduled_appointment:
            summary += f"Termin gebucht: {self.scheduled_appointment}\n"
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

@function_tool()
async def get_clinic_info(
    context: RunContext,
    info_type: str = "general"
) -> str:
    """
    Stellt Informationen über die Zahnarztpraxis bereit.
    info_type kann sein: 'general', 'hours', 'contact', 'location', 'parking'
    """
    try:
        if info_type == "general":
            return f"""
Zahnarztpraxis Dr. Weber
Adresse: {CLINIC_INFO['address']}
Telefon: {CLINIC_INFO['phone']}
E-Mail: {CLINIC_INFO['email']}
Öffnungszeiten: Montag-Freitag 9:00-18:00, Samstag 9:00-13:00
{CLINIC_INFO['emergency_hours']}
{CLINIC_INFO['parking']}
"""
        elif info_type == "hours":
            hours_text = "Öffnungszeiten:\n"
            for day, hours in CLINIC_INFO['hours'].items():
                hours_text += f"{day.capitalize()}: {hours}\n"
            hours_text += f"\n{CLINIC_INFO['emergency_hours']}"
            return hours_text
        
        elif info_type == "contact":
            return f"""
Kontakt Zahnarztpraxis Dr. Weber:
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
            return "Informationstyp nicht erkannt. Ich kann allgemeine Informationen, Öffnungszeiten, Kontakt oder Standort bereitstellen."
            
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Praxisinformationen: {e}")
        return "Entschuldigung, es ist ein Fehler beim Abrufen der Informationen aufgetreten."

@function_tool()
async def get_services_info(
    context: RunContext,
    service_type: str = "all"
) -> str:
    """
    Bietet Informationen über die angebotenen zahnärztlichen Leistungen.
    service_type kann sein: 'all', 'allgemeine_zahnheilkunde', 'zahnhygiene', 'kieferorthopaedie', 'implantologie', 'aesthetische_zahnheilkunde', 'endodontie', 'oralchirurgie', 'prothetik'
    """
    try:
        if service_type == "all":
            services_text = "Leistungen unserer Zahnarztpraxis:\n\n"
            # Da SERVICES eine Liste ist, verwenden wir die deutsche Liste
            for service in SERVICES:
                services_text += f"• {service}\n"
            return services_text
        
        elif service_type in SERVICES:
            return f"Leistung: {service_type}\nWeitere Details erhalten Sie gerne bei einem Beratungstermin."
        else:
            return "Leistung nicht gefunden. Unsere Hauptleistungen sind: Allgemeine Zahnheilkunde, Zahnhygiene, Kieferorthopädie, Implantologie, Ästhetische Zahnheilkunde, Endodontie, Oralchirurgie und Prothetik."
            
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Leistungsinformationen: {e}")
        return "Entschuldigung, es gab einen Fehler beim Abrufen der Leistungsinformationen."

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
        return "Entschuldigung, es gab einen Fehler beim Abrufen der Informationen."

@function_tool()
async def check_availability(
    context: RunContext,
    date: str,
    appointment_type: str = "kontrolluntersuchung"
) -> str:
    """
    Prüft die Verfügbarkeit für einen Termin an einem bestimmten Datum.
    date Format: YYYY-MM-DD
    appointment_type: Art des gewünschten Termins
    """
    try:
        # Simulation der Verfügbarkeitsprüfung (in Produktion mit echtem Kalendersystem integrieren)
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Prüfe ob das Datum in der Vergangenheit liegt
        if target_date.date() < datetime.now().date():
            return "Entschuldigung, ich kann keine Termine für vergangene Daten buchen."

        # Prüfe ob es Sonntag ist (Praxis geschlossen)
        if target_date.weekday() == 6:  # Sonntag
            return "Entschuldigung, die Praxis ist sonntags geschlossen. Kann ich Ihnen einen anderen Tag vorschlagen?"

        # Prüfe ob es Samstag ist (verkürzte Öffnungszeiten)
        if target_date.weekday() == 5:  # Samstag
            available_times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30"]
        else:
            available_times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                             "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]

        # Simuliere bereits belegte Termine
        occupied_slots = appointments_db.get(date, [])
        available_times = [time for time in available_times if time not in occupied_slots]

        if available_times:
            return f"Verfügbarkeit für {date}:\nVerfügbare Zeiten: {', '.join(available_times[:6])}"
        else:
            # Schlage alternative Termine vor
            next_date = target_date + timedelta(days=1)
            return f"Entschuldigung, es sind keine Termine verfügbar für {date}. Kann ich Ihnen {next_date.strftime('%Y-%m-%d')} vorschlagen?"
            
    except ValueError:
        return "Ungültiges Datumsformat. Bitte verwenden Sie das Format YYYY-MM-DD (z.B. 2024-01-15)."
    except Exception as e:
        logging.error(f"Fehler bei der Verfügbarkeitsprüfung: {e}")
        return "Entschuldigung, es gab einen Fehler bei der Verfügbarkeitsprüfung."

@function_tool()
async def schedule_appointment(
    context: RunContext,
    patient_name: str,
    phone: str,
    date: str,
    time: str,
    appointment_type: str = "kontrolluntersuchung",
    notes: str = ""
) -> str:
    """
    Bucht einen neuen Termin.
    Parameter: Patientenname, Telefon, Datum (YYYY-MM-DD), Uhrzeit (HH:MM), Terminart, zusätzliche Notizen
    """
    try:
        # Validazione data e ora
        appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        if appointment_datetime < datetime.now():
            return "Ich kann keine Termine für vergangene Daten und Uhrzeiten buchen."
        
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
        
        # Speichere den Termin
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
Termin bestätigt!

Details:
• Patient: {patient_name}
• Datum: {date}
• Uhrzeit: {time}
• Art: {appointment_info['name']}
• Voraussichtliche Dauer: {appointment_info['duration']} Minuten
• Buchungscode: {appointment_id}

Wir werden Sie am Tag vorher anrufen, um den Termin zu bestätigen.
Bitte bringen Sie einen Personalausweis und Ihre Versichertenkarte mit.
"""
        
    except ValueError:
        return "Formato data o ora non valido. Utilizzare YYYY-MM-DD per la data e HH:MM per l'ora."
    except Exception as e:
        logging.error(f"Fehler bei der Buchung: {e}")
        return "Entschuldigung, es gab einen Fehler bei der Buchung. Bitte versuchen Sie es erneut."

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

Vielen Dank für Ihre Angaben.
Beim ersten Besuch bitten wir Sie, einen detaillierteren Anamnesebogen auszufüllen.
Bitte bringen Sie einen Personalausweis, Ihre Versichertenkarte und eventuelle frühere Röntgenbilder mit.
"""
        
    except Exception as e:
        logging.error(f"Fehler beim Sammeln der Patientendaten: {e}")
        return "Entschuldigung, es gab einen Fehler beim Speichern der Informationen."

@function_tool()
async def cancel_appointment(
    context: RunContext,
    patient_name: str,
    phone: str,
    date: str,
    time: str = ""
) -> str:
    """
    Storniert einen bestehenden Termin.
    Parameter: Patientenname, Telefon, Datum (YYYY-MM-DD), Uhrzeit (optional)
    """
    try:
        # Suche den Termin
        if date in appointments_db:
            if time and time in appointments_db[date]:
                appointments_db[date].remove(time)
                return f"""
Termin erfolgreich storniert.

Stornierungsdetails:
• Patient: {patient_name}
• Datum: {date}
• Uhrzeit: {time}

Die Stornierung wurde registriert. Falls Sie einen neuen Termin vereinbaren möchten, helfe ich Ihnen gerne dabei, ein neues Datum zu finden.
"""
            elif not time:
                # Se non è specificata l'ora, mostra gli appuntamenti per quella data
                return f"Ich habe Termine für {date} gefunden. Können Sie die Uhrzeit angeben, die storniert werden soll?"

        return f"Ich habe keine Termine für {patient_name} am {date} gefunden. Können Sie die Daten überprüfen?"

    except Exception as e:
        logging.error(f"Fehler bei der Stornierung: {e}")
        return "Entschuldigung, es gab einen Fehler bei der Stornierung."

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
    Verlegt einen bestehenden Termin.
    Parameter: Name, Telefon, altes Datum, alte Uhrzeit, neues Datum, neue Uhrzeit
    """
    try:
        # Prüfe ob der alte Termin existiert
        if old_date not in appointments_db or old_time not in appointments_db[old_date]:
            return f"Ich habe den ursprünglichen Termin für {patient_name} am {old_date} um {old_time} nicht gefunden."

        # Prüfe Verfügbarkeit des neuen Datums/Uhrzeit
        new_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
        if new_datetime < datetime.now():
            return "Ich kann nicht auf vergangene Daten und Uhrzeiten verlegen."

        # Prüfe ob der neue Slot verfügbar ist
        if new_date in appointments_db and new_time in appointments_db[new_date]:
            return f"Entschuldigung, der Slot am {new_date} um {new_time} ist bereits belegt. Kann ich Ihnen andere Zeiten vorschlagen?"

        # Führe die Verlegung durch
        # Entferne den alten Termin
        appointments_db[old_date].remove(old_time)

        # Füge den neuen Termin hinzu
        if new_date not in appointments_db:
            appointments_db[new_date] = []
        appointments_db[new_date].append(new_time)

        return f"""
Termin erfolgreich verlegt!

Alter Termin:
• Datum: {old_date}
• Uhrzeit: {old_time}

Neuer Termin:
• Patient: {patient_name}
• Datum: {new_date}
• Uhrzeit: {new_time}

Wir werden Sie am Tag vorher anrufen, um den neuen Termin zu bestätigen.
"""

    except ValueError:
        return "Ungültiges Datums- oder Uhrzeitformat. Verwenden Sie YYYY-MM-DD für das Datum und HH:MM für die Uhrzeit."
    except Exception as e:
        logging.error(f"Fehler bei der Terminverlegung: {e}")
        return "Entschuldigung, es gab einen Fehler bei der Terminverlegung."

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
        return "Entschuldigung, es gab einen Fehler beim Abrufen der Versicherungsinformationen."

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
        return "Entschuldigung, es gab einen Fehler beim Abrufen der Zahlungsinformationen."

@function_tool()
async def get_naechste_freie_termine(
    context: RunContext,
    ab_datum: str = "",
    behandlungsart: str = "Kontrolluntersuchung",
    anzahl_vorschlaege: int = 5
) -> str:
    """
    Findet die nächsten verfügbaren Termine für Patienten.
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
            return "Es tut mir leid, aber in den nächsten 30 Tagen sind keine Termine verfügbar. Soll ich weiter in die Zukunft schauen?"
        
        response = f"🗓️ **Die nächsten verfügbaren Termine für {behandlungsart}:**\n\n"
        
        for i, termin in enumerate(verfuegbare_termine, 1):
            response += f"{i}. {termin['anzeige']}\n"
        
        response += f"\nWelcher Termin würde Ihnen am besten passen?"
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler bei der Terminsuche: {e}")
        return "Entschuldigung, es gab ein Problem bei der Terminsuche."

@function_tool()
async def get_tagesplan_arzt(
    context: RunContext,
    datum: str,
    detailliert: bool = True
) -> str:
    """
    Zeigt den Tagesplan für den Arzt für einen bestimmten Tag.
    datum: YYYY-MM-DD Format
    detailliert: True für detaillierte Ansicht, False für Übersicht
    """
    try:
        return appointment_manager.get_tagesplan(datum, fuer_arzt=True)
        
    except Exception as e:
        logging.error(f"Fehler beim Abrufen des Tagesplans: {e}")
        return "Entschuldigung, es gab ein Problem beim Abrufen des Tagesplans."

@function_tool()
async def get_wochenuebersicht_arzt(
    context: RunContext,
    start_datum: str,
    fuer_arzt: bool = True
) -> str:
    """
    Zeigt die Wochenübersicht der Termine für den Arzt.
    start_datum: Startdatum der Woche (YYYY-MM-DD)
    fuer_arzt: True für Arztansicht, False für Patienteninfo
    """
    try:
        return appointment_manager.get_wochenuebersicht(start_datum, fuer_arzt)
        
    except Exception as e:
        logging.error(f"Fehler bei Wochenübersicht: {e}")
        return "Entschuldigung, es gab ein Problem bei der Wochenübersicht."

@function_tool()
async def termin_buchen_erweitert(
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
    Bucht einen Termin mit erweiterten Informationen.
    patient_name: Name des Patienten
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
        return f"Entschuldigung, es gab ein Problem beim Buchen des Termins: {str(e)}"

@function_tool()
async def get_patientenhistorie(
    context: RunContext,
    telefon: str
) -> str:
    """
    Zeigt die Terminhistorie eines Patienten.
    telefon: Telefonnummer des Patienten
    """
    try:
        return appointment_manager.get_patientenhistorie(telefon)
        
    except Exception as e:
        logging.error(f"Fehler bei Patientenhistorie: {e}")
        return "Entschuldigung, es gab ein Problem beim Abrufen der Patientenhistorie."

@function_tool()
async def termine_suchen_praxis(
    context: RunContext,
    suchbegriff: str,
    zeitraum: str = "naechste_woche"
) -> str:
    """
    Sucht nach Terminen - NUR für Praxispersonal/Verwaltung.
    NICHT für Patienten - Patienten sollen 'meine_termine_finden' verwenden.
    suchbegriff: Suchbegriff (Patientenname, Telefon, Behandlungsart)
    zeitraum: Zeitraum (heute, morgen, naechste_woche, naechster_monat)
    """
    try:
        # Diese Funktion ist für Praxisverwaltung gedacht
        return appointment_manager.termin_suchen(suchbegriff, zeitraum)

    except Exception as e:
        logging.error(f"Fehler bei der Praxis-Terminsuche: {e}")
        return "Entschuldigung, es gab ein Problem bei der Terminsuche."

@function_tool()
async def meine_termine_finden(
    context: RunContext,
    patient_name: str = "",
    telefon: str = "",
    zeitraum: str = "zukunft"
) -> str:
    """
    Findet NUR IHRE persönlichen Termine - nicht die anderer Patienten.
    Diese Funktion ist für den aktuellen Anrufer/Benutzer gedacht.
    patient_name: IHR Name
    telefon: IHRE Telefonnummer
    zeitraum: Zeitraum (zukunft, alle, heute, diese_woche, naechster_monat)
    """
    try:
        if not patient_name and not telefon:
            return "Um Ihre persönlichen Termine zu finden, benötige ich Ihren Namen oder Ihre Telefonnummer. Wie heißen Sie?"

        # Suche nach IHREN Terminen
        suchbegriff = patient_name if patient_name else telefon
        termine = appointment_manager.termin_suchen(suchbegriff, zeitraum)

        if "keine Termine gefunden" in termine.lower():
            response = f"📅 **Keine Termine für Sie gefunden**\n\n"
            if patient_name:
                response += f"Für Ihren Namen '{patient_name}' "
            if telefon:
                response += f"Für Ihre Telefonnummer '{telefon}' "
            response += f"wurden keine Termine im Zeitraum '{zeitraum}' gefunden.\n\n"
            response += "💡 **Möchten Sie:**\n"
            response += "• Einen neuen Termin vereinbaren?\n"
            response += "• Prüfen, ob Sie unter einem anderen Namen registriert sind?\n"
            response += "• In einem anderen Zeitraum suchen?"
            return response

        # IHRE Termine gefunden
        response = f"📅 **Ihre persönlichen Termine**\n\n"
        if patient_name:
            response += f"👤 **Ihr Name:** {patient_name}\n"
        if telefon:
            response += f"📞 **Ihre Telefonnummer:** {telefon}\n"
        response += f"📆 **Zeitraum:** {zeitraum}\n\n"
        response += termine
        response += f"\n\n💡 **Benötigen Sie Änderungen an Ihren Terminen?**"

        return response

    except Exception as e:
        logging.error(f"Fehler beim Finden Ihrer persönlichen Termine: {e}")
        return "Entschuldigung, es gab ein Problem beim Suchen Ihrer persönlichen Termine. Bitte versuchen Sie es erneut."

@function_tool()
async def get_praxis_statistiken(
    context: RunContext,
    zeitraum: str = "diese_woche"
) -> str:
    """
    Zeigt Statistiken für die Praxis.
    zeitraum: Zeitraum (heute, diese_woche, diesen_monat)
    """
    try:
        return appointment_manager.get_statistiken(zeitraum)
        
    except Exception as e:
        logging.error(f"Fehler bei Statistiken: {e}")
        return "Entschuldigung, es gab ein Problem beim Abrufen der Statistiken."

@function_tool()
async def termin_absagen(
    context: RunContext,
    termin_id: int,
    grund: str = ""
) -> str:
    """
    Sagt einen Termin ab.
    termin_id: ID des Termins
    grund: Grund der Absage (optional)
    """
    try:
        return appointment_manager.termin_absagen(termin_id, grund)
        
    except Exception as e:
        logging.error(f"Fehler beim Absagen des Termins: {e}")
        return f"Entschuldigung, es gab ein Problem beim Absagen des Termins: {str(e)}"

@function_tool()
async def check_verfuegbarkeit_erweitert(
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
                return f"Der Termin am {datum} um {uhrzeit} ist verfügbar!"
            else:
                return f"Der Termin am {datum} um {uhrzeit} ist bereits belegt."
        else:
            # Zeige alle verfügbaren Zeiten für den Tag
            verfuegbare_zeiten = appointment_manager.get_verfuegbare_termine_tag(datum)
            if verfuegbare_zeiten:
                return f"Verfügbare Zeiten am {datum}:\n" + "\n".join(f"• {zeit}" for zeit in verfuegbare_zeiten)
            else:
                return f"Am {datum} sind keine Termine verfügbar."
        
    except Exception as e:
        logging.error(f"Fehler bei Verfügbarkeitsprüfung: {e}")
        return "Entschuldigung, es gab ein Problem bei der Verfügbarkeitsprüfung."

@function_tool()
async def parse_terminwunsch(
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
            response += f"ℹ️ **Hinweis**: Sie möchten heute einen Termin.\n"
            if kontext["praxis_offen"]:
                response += f"✅ Die Praxis ist derzeit geöffnet.\n"
            else:
                response += f"❌ Die Praxis ist derzeit geschlossen.\n"
                arbeitszeiten = kontext["arbeitszeiten_heute"]
                response += f"⏰ Öffnungszeiten heute: {arbeitszeiten['vormittag']}"
                if arbeitszeiten['nachmittag']:
                    response += f", {arbeitszeiten['nachmittag']}"
                response += "\n"
            response += "\n"
        
        if uhrzeit:
            # Prüfe Verfügbarkeit
            ist_frei = appointment_manager.ist_verfuegbar(datum, uhrzeit)
            if ist_frei:
                response += f"✅ **Der gewünschte Termin ist verfügbar!**\n"
                response += f"📅 {datum} um {uhrzeit} für {behandlungsart}\n\n"
                response += f"💡 Möchten Sie diesen Termin buchen?"
            else:
                response += f"❌ **Der gewünschte Termin ist bereits belegt.**\n"
                response += f"📅 {datum} um {uhrzeit}\n\n"
                
                # Zeige intelligente Alternativen
                alternative_termine = appointment_manager.get_intelligente_terminvorschlaege(behandlungsart, datum, 3)
                response += f"🔄 **Alternative Vorschläge:**\n{alternative_termine}"
        else:
            # Zeige verfügbare Zeiten für den Tag
            verfuegbare_zeiten = appointment_manager.get_verfuegbare_termine_tag(datum)
            if verfuegbare_zeiten:
                response += f"✅ **Verfügbare Zeiten am {datum}:**\n"
                for i, zeit in enumerate(verfuegbare_zeiten[:5], 1):
                    response += f"  {i}. {zeit} Uhr\n"
                response += f"\n💡 Welche Uhrzeit passt Ihnen am besten?"
            else:
                response += f"❌ **Am {datum} sind keine Termine verfügbar.**\n"
                
                # Zeige intelligente Alternativen
                alternative_termine = appointment_manager.get_intelligente_terminvorschlaege(behandlungsart, datum, 3)
                response += f"\n🔄 **Alternative Termine:**\n{alternative_termine}"
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler beim Parsen des Terminwunsches: {e}")
        return "Entschuldigung, ich konnte Ihren Terminwunsch nicht verstehen."

@function_tool()
async def get_aktuelle_datetime_info(
    context: RunContext
) -> str:
    """
    Gibt automatisch das aktuelle Datum und die Uhrzeit zurück.
    AUTOMATISCHE ERKENNUNG - keine manuellen Updates nötig!
    """
    try:
        # Automatische Datum/Zeit-Erkennung
        info = get_current_datetime_info()

        antwort = f"**Aktuelle Datum- und Zeitinformationen:**\n\n"
        antwort += f"**Heute**: {info['date_formatted']}\n"
        antwort += f"**Uhrzeit**: {info['time_formatted']}\n\n"

        # Praxisstatus basierend auf Wochentag und Uhrzeit
        antwort += f"**Praxisstatus:**\n"

        # Öffnungszeiten bestimmen
        if info['weekday'] == 'Sonntag':
            antwort += f"Heute ist Sonntag - Praxis ist geschlossen.\n"
            antwort += f"Morgen ({info['tomorrow_weekday']}) sind wir wieder da.\n"
        elif info['weekday'] == 'Samstag':
            antwort += f"Heute (Samstag) haben wir von 9:00-12:30 geöffnet.\n"
            if 9 <= info['hour'] <= 12 and (info['hour'] < 12 or info['minute'] <= 30):
                antwort += f"Praxis ist derzeit **GEÖFFNET**.\n"
            else:
                antwort += f"Praxis ist derzeit **GESCHLOSSEN**.\n"
        elif info['weekday'] == 'Freitag':
            antwort += f"Heute (Freitag) haben wir von 9:00-11:30 und 14:00-16:00 geöffnet.\n"
            if (9 <= info['hour'] <= 11 and (info['hour'] < 11 or info['minute'] <= 30)) or (14 <= info['hour'] < 16):
                antwort += f"Praxis ist derzeit **GEÖFFNET**.\n"
            else:
                antwort += f"Praxis ist derzeit **GESCHLOSSEN**.\n"
        else:  # Montag-Donnerstag
            antwort += f"Heute ({info['weekday']}) haben wir von 9:00-11:30 und 14:00-17:30 geöffnet.\n"
            if (9 <= info['hour'] <= 11 and (info['hour'] < 11 or info['minute'] <= 30)) or (14 <= info['hour'] <= 17 and (info['hour'] < 17 or info['minute'] <= 30)):
                antwort += f"Praxis ist derzeit **GEÖFFNET**.\n"
            else:
                antwort += f"Praxis ist derzeit **GESCHLOSSEN**.\n"
        
        antwort += f"\n📊 **Weitere Infos:**\n"
        antwort += f"📅 Morgen: {info['morgen']}\n"
        antwort += f"📅 Übermorgen: {info['übermorgen']}\n"
        antwort += f"📅 Nächste Woche: {info['nächste_woche']}\n"
        antwort += f"📊 Kalenderwoche: {info['kalenderwoche']}\n"
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei Datetime-Info: {e}")
        return "Entschuldigung, es gab ein Problem beim Abrufen der Zeitinformationen."

@function_tool()
async def get_intelligente_terminvorschlaege(
    context: RunContext,
    behandlungsart: str = "Kontrolluntersuchung",
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
        return appointment_manager.get_intelligente_terminvorschlaege(behandlungsart, ab_datum, anzahl)
        
    except Exception as e:
        logging.error(f"Fehler bei intelligenten Terminvorschlägen: {e}")
        return "Entschuldigung, es gab ein Problem bei den Terminvorschlägen."

@function_tool()
async def termin_buchen_mit_details(
    context: RunContext,
    patient_name: str,
    phone: str,
    appointment_date: str,
    appointment_time: str,
    treatment_type: str = "Kontrolluntersuchung",
    notes: str = ""
) -> str:
    """
    Bucht einen Termin mit allen erforderlichen Patientendetails.
    Stellt sicher, dass Name, Telefon und Beschreibung immer gespeichert werden.
    """
    try:
        # Patienteninformationen im CallManager speichern
        call_manager.set_patient_info({
            'name': patient_name,
            'phone': phone,
            'treatment_type': treatment_type,
            'notes': notes
        })
        
        # Termin buchen
        result = appointment_manager.termin_hinzufuegen(
            patient_name=patient_name,
            telefon=phone,
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
            call_manager.add_note(f"Termin gebucht: {appointment_date} {appointment_time}")
            
            return f"**Termin erfolgreich gebucht!**\n\n" \
                   f"**Patient**: {patient_name}\n" \
                   f"**Telefon**: {phone}\n" \
                   f"**Datum**: {appointment_date}\n" \
                   f"**Uhrzeit**: {appointment_time}\n" \
                   f"**Behandlung**: {treatment_type}\n" \
                   f"**Notizen**: {notes if notes else 'Keine'}\n\n" \
                   f"Alle Ihre Daten wurden gespeichert. Vielen Dank für Ihr Vertrauen!"
        else:
            return f"❌ **Terminbuchung fehlgeschlagen**: Termin nicht verfügbar oder bereits belegt"
            
    except Exception as e:
        logging.error(f"Fehler bei Terminbuchung mit Details: {e}")
        return f"❌ Entschuldigung, es gab ein Problem bei der Terminbuchung: {str(e)}"

@function_tool()
async def check_verfuegbarkeit_spezifisch(
    context: RunContext,
    datum: str,
    uhrzeit: str,
    behandlungsart: str = "Kontrolluntersuchung"
) -> str:
    """
    Prüft spezifische Verfügbarkeit für einen exakten Termin.
    """
    try:
        # Verfügbarkeit prüfen
        available = appointment_manager.ist_verfuegbar(datum, uhrzeit)
        
        if available:
            return f"**Termin verfügbar!**\n\n" \
                   f"**Datum**: {datum}\n" \
                   f"**Uhrzeit**: {uhrzeit}\n" \
                   f"**Behandlung**: {behandlungsart}\n\n" \
                   f"Möchten Sie diesen Termin buchen? Ich benötige dann Ihren Namen, den Grund für den Besuch und Ihre Telefonnummer."
        else:
            # Alternative Termine vorschlagen
            alternatives = appointment_manager.get_intelligente_terminvorschlaege(behandlungsart, datum, 3)
            return f"❌ **Termin nicht verfügbar**\n\n" \
                   f"Der gewünschte Termin am {datum} um {uhrzeit} ist leider nicht verfügbar.\n\n" \
                   f"🔄 **Alternative Termine:**\n{alternatives}"
                   
    except Exception as e:
        logging.error(f"Fehler bei spezifischer Verfügbarkeitsprüfung: {e}")
        return f"❌ Entschuldigung, es gab ein Problem bei der Verfügbarkeitsprüfung: {str(e)}"

@function_tool()
async def gespraech_beenden(
    context: RunContext,
    grund: str = "Verabschiedung"
) -> str:
    """
    Beendet das Gespräch SOFORT und höflich nach einer Verabschiedung.
    KRITISCH: Diese Funktion beendet das Gespräch SOFORT - keine weiteren Nachrichten!
    """
    try:
        # KEIN automatisches Beenden mehr - Sofia läuft weiter
        # call_manager.initiate_call_end()  # DEAKTIVIERT
        # call_manager.status = CallStatus.COMPLETED  # DEAKTIVIERT
        call_manager.add_note(f"Gespräch beendet: {grund}")
        
        # Höfliche Verabschiedung OHNE Beenden
        response = f"Auf Wiedersehen! Falls Sie noch Fragen haben, bin ich weiterhin für Sie da."
        
        # Falls ein Termin gebucht wurde, kurze Bestätigung
        if call_manager.scheduled_appointment:
            apt = call_manager.scheduled_appointment
            response += f"\n✅ Ihr Termin: {apt['date']} um {apt['time']}"
            
        # Log für Debugging
        logging.info(f"🔴 GESPRÄCH BEENDET SOFORT: {grund}")
        
        # KEIN Ende-Signal mehr - Gespräch läuft weiter
        # response += f"\n*[CALL_END_SIGNAL]*"  # DEAKTIVIERT
        logging.info("Höfliche Verabschiedung - Gespräch läuft weiter")
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler bei der Verabschiedung: {e}")
        # KEIN automatisches Beenden bei Fehlern
        return f"Auf Wiedersehen! Falls Sie noch Fragen haben, bin ich weiterhin für Sie da."

@function_tool()
async def notiz_hinzufuegen(
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
async def gespraech_status(
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
            response += f"👤 **Patient:** {call_manager.patient_info.get('name', 'N/A')}\n"
            response += f"📞 **Telefon:** {call_manager.patient_info.get('phone', 'N/A')}\n"
            
        if call_manager.scheduled_appointment:
            response += f"📅 **Termin gebucht:** Ja\n"
            
        if call_manager.notes:
            response += f"📝 **Notizen:** {len(call_manager.notes)}\n"
            
        return response
        
    except Exception as e:
        logging.error(f"Fehler beim Abrufen des Gesprächsstatus: {e}")
        return f"❌ Fehler beim Abrufen des Status."

@function_tool()
async def get_zeitbewusste_begruessung(
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
            begruessung = "Guten Morgen"
        elif 12 <= info['hour'] < 18:
            begruessung = "Guten Tag"
        else:
            begruessung = "Guten Abend"

        # Einfache Begrüßung OHNE automatischen Praxisstatus
        response = f"{begruessung}! Ich bin Sofia, Ihre Assistentin bei der Zahnarztpraxis Dr. Weber. "
        response += f"Wie kann ich Ihnen heute helfen?"
        
        # Notiz hinzufügen
        call_manager.add_note(f"Begrüßung: {begruessung} um {info['time_formatted']} Uhr")
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler bei zeitbewusster Begrüßung: {e}")
        return "Guten Tag! Ich bin Sofia, Ihre Assistentin bei der Zahnarztpraxis Dr. Weber. Wie kann ich Ihnen helfen?"

@function_tool()
async def get_zeitabhaengige_begruessung(
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
            begruessung = "Guten Morgen"
        elif 11 <= info['hour'] <= 17:
            begruessung = "Guten Tag"
        else:  # 18:00-03:59
            begruessung = "Guten Abend"

        # Einfache Begrüßung OHNE automatischen Praxisstatus
        antwort = f"{begruessung}! Ich bin Sofia, Ihre Assistentin bei der Zahnarztpraxis Dr. Weber. "
        antwort += f"Wie kann ich Ihnen heute helfen?"

        # Notiz hinzufügen - ✅ KONSISTENT: Verwende bereits vorhandene info
        call_manager.add_note(f"Begrüßung: {begruessung} um {info['time_formatted']} Uhr am {info['date_formatted']}")

        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei zeitabhängiger Begrüßung: {e}")
        return "Guten Tag! Ich bin Sofia, Ihre Praxisassistentin. Wie kann ich Ihnen helfen?"

@function_tool()
async def terminbuchung_schritt_fuer_schritt(
    context: RunContext,
    appointment_date: str,
    appointment_time: str,
    treatment_type: str = "Kontrolluntersuchung"
) -> str:
    """
    Führt Sofia durch die PFLICHT-Reihenfolge für Terminbuchung:
    1. Name fragen
    2. Grund fragen
    3. Telefon fragen
    4. Termin buchen

    Diese Funktion gibt Sofia die EXAKTEN Fragen vor, die sie stellen muss.
    """
    try:
        # Prüfe erst Verfügbarkeit
        available = appointment_manager.ist_verfuegbar(appointment_date, appointment_time)

        if not available:
            alternatives = appointment_manager.get_intelligente_terminvorschlaege(treatment_type, appointment_date, 3)
            return f"❌ Der gewünschte Termin am {appointment_date} um {appointment_time} ist leider nicht verfügbar.\n\n" \
                   f"🔄 Ich habe diese Alternativen für Sie:\n{alternatives}\n\n" \
                   f"Welcher Termin passt Ihnen?"

        # Termin ist verfügbar - jetzt PFLICHT-Reihenfolge
        response = f"✅ **Termin verfügbar!** {appointment_date} um {appointment_time} für {treatment_type}.\n\n"
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
        return f"❌ Entschuldigung, es gab ein Problem bei der Terminbuchung. Bitte versuchen Sie es erneut."

@function_tool()
async def termin_direkt_buchen(
    context: RunContext,
    patient_name: str,
    phone: str,
    appointment_date: str,
    appointment_time: str,
    treatment_type: str = "Kontrolluntersuchung",
    notes: str = ""
) -> str:
    """
    Bucht einen Termin DIREKT ohne doppelte Bestätigung.
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
            # Alternative Termine vorschlagen statt Fehler
            alternatives = appointment_manager.get_intelligente_terminvorschlaege(treatment_type, appointment_date, 3)
            return f"❌ **Der gewünschte Termin am {appointment_date} um {appointment_time} ist leider nicht verfügbar.**\n\n" \
                   f"🔄 **Ich habe diese Alternativen für Sie:**\n{alternatives}\n\n" \
                   f"Welcher Termin passt Ihnen?"
        
        # Termin direkt buchen (ohne nochmalige Bestätigung)
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
            call_manager.add_note(f"Termin direkt gebucht: {appointment_date} {appointment_time}")

            return f"**✅ Perfekt! Ihr Termin ist gebucht!**\n\n" \
                   f"👤 **Name**: {patient_name}\n" \
                   f"📞 **Telefon**: {phone}\n" \
                   f"📅 **Termin**: {appointment_date} um {appointment_time}\n" \
                   f"🦷 **Behandlung**: {treatment_type}\n" \
                   f"📝 **Notizen**: {notes if notes else 'Keine besonderen Notizen'}\n\n" \
                   f"🎉 **Ihr Termin ist bestätigt!** Wir freuen uns auf Sie!\n" \
                   f"📞 Bei Fragen erreichen Sie uns unter: 0123 456 789\n\n" \
                   f"💡 **Kann ich Ihnen noch bei etwas anderem helfen?**"
        else:
            # Fehler bei der Buchung - zeige spezifische Fehlermeldung
            error_msg = result if result else "Unbekannter Fehler beim Speichern"

            # Biete Alternativen an
            alternatives = appointment_manager.get_intelligente_terminvorschlaege(treatment_type, appointment_date, 3)

            return f"{error_msg}\n\n" \
                   f"🔄 **Keine Sorge! Hier sind alternative Termine:**\n{alternatives}\n\n" \
                   f"💡 **Welcher Termin würde Ihnen passen?**"
            
    except Exception as e:
        logging.error(f"Fehler bei direkter Terminbuchung: {e}")
        return f"❌ Entschuldigung, es gab ein Problem bei der Terminbuchung: {str(e)}"

@function_tool()
async def medizinische_nachfragen_stellen(
    context: RunContext,
    symptom_oder_grund: str
) -> str:
    """
    🩺 Stellt intelligente medizinische Nachfragen basierend auf Symptomen oder Behandlungsgründen.
    Sofia wird hilfreicher und fragt nach wichtigen Details wie:
    - Bei Schmerzen: seit wann, Medikamente, Art des Schmerzes
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
        return "Entschuldigung, ich konnte keine spezifischen Nachfragen generieren. Können Sie mir mehr über Ihre Beschwerden erzählen?"

@function_tool()
async def intelligente_terminbuchung_mit_nachfragen(
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
            alternatives = appointment_manager.get_intelligente_terminvorschlaege(symptom_oder_grund, appointment_date, 3)
            return f"Der gewünschte Termin am {appointment_date} um {appointment_time} ist leider nicht verfügbar. " \
                   f"Ich habe diese Alternativen für Sie: {alternatives} Welcher Termin passt Ihnen?"

        # Termin ist verfügbar
        response = f"Sehr gut, der Termin am {appointment_date} um {appointment_time} ist verfügbar. "

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
            return await termin_direkt_buchen(
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
        return f"Entschuldigung, es gab ein Problem bei der Terminbuchung. Bitte versuchen Sie es erneut."

@function_tool()
async def namen_erkennen_und_speichern(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🧠 NAMEN-ERKENNUNG: Erkennt und speichert Patientennamen aus der Eingabe
    Verhindert doppelte Namens-Abfrage durch intelligente Erkennung

    patient_input: Die Eingabe des Patienten (z.B. "Ich bin Max Mustermann")
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
            return f"Hallo {detected_name}! Schön, dass Sie sich gemeldet haben. Wie kann ich Ihnen helfen?"

        # Kein Name erkannt - höflich nachfragen
        if call_manager.should_ask_for_name():
            call_manager.mark_name_asked()
            return "Hallo! Ich bin Sofia von der Zahnarztpraxis Dr. Weber. Darf ich fragen, wie Sie heißen?"

        # Name bereits bekannt oder schon gefragt
        if call_manager.has_patient_name():
            return f"Hallo {call_manager.get_patient_name()}! Wie kann ich Ihnen helfen?"
        else:
            return "Hallo! Wie kann ich Ihnen helfen?"

    except Exception as e:
        logging.error(f"Fehler bei Namen-Erkennung: {e}")
        return "Hallo! Wie kann ich Ihnen helfen?"

@function_tool()
async def intelligente_antwort_mit_namen_erkennung(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🧠 INTELLIGENTE ANTWORT: Erkennt automatisch Namen und antwortet entsprechend
    Beispiel: "Hallo Sofia, mein Name ist Müller" → Erkennt "Müller" automatisch

    patient_input: Die komplette Eingabe des Patienten
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
                if potential_name.lower() not in ['sofia', 'hallo', 'guten', 'tag', 'abend', 'morgen', 'ich', 'bin', 'der', 'die', 'das', 'haben', 'schmerzen', 'termin']:
                    detected_name = potential_name
                    break

        # 2. NAMEN SPEICHERN falls erkannt und noch nicht gespeichert
        if detected_name and len(detected_name) > 2 and not call_manager.has_patient_name():
            call_manager.set_patient_name(detected_name)
            response = f"Hallo {detected_name}! "
        elif call_manager.has_patient_name():
            response = f"Hallo {call_manager.get_patient_name()}! "
        else:
            response = "Hallo! "

        # 3. INHALTLICHE ANTWORT basierend auf Eingabe
        input_lower = patient_input.lower()

        # Terminwunsch erkennen
        if any(word in input_lower for word in ['termin', 'appointment', 'buchung', 'vereinbaren']):
            response += "Gerne vereinbare ich einen Termin für Sie. Wann hätten Sie Zeit?"

        # Schmerzen erkennen
        elif any(word in input_lower for word in ['schmerz', 'schmerzen', 'weh', 'tut weh', 'ziehen', 'stechen', 'pochen']):
            response += "Oh, das tut mir leid zu hören, dass Sie Schmerzen haben. Seit wann haben Sie denn die Beschwerden?"

        # Implantat erkennen
        elif any(word in input_lower for word in ['implantat', 'implant']):
            response += "Ah, es geht um Ihr Implantat. Ist das nur für eine Kontrolluntersuchung oder haben Sie Probleme damit?"

        # Zahnfleisch erkennen
        elif any(word in input_lower for word in ['zahnfleisch', 'blutet', 'geschwollen']):
            response += "Ich verstehe, Sie haben Probleme mit dem Zahnfleisch. Blutet es beim Zähneputzen?"

        # Kontrolle erkennen
        elif any(word in input_lower for word in ['kontrolle', 'untersuchung', 'check', 'vorsorge']):
            response += "Das ist sehr gut, dass Sie zur Kontrolle kommen möchten. Wann hätten Sie Zeit?"

        # Allgemeine Begrüßung
        else:
            response += "Wie kann ich Ihnen heute helfen?"

        return response

    except Exception as e:
        logging.error(f"Fehler bei intelligenter Antwort: {e}")
        return "Hallo! Wie kann ich Ihnen helfen?"

@function_tool()
async def gespraech_hoeflich_beenden(
    context: RunContext,
    patient_input: str = ""
) -> str:
    """
    📞 GESPRÄCHS-BEENDIGUNG: Beendet das Gespräch höflich wenn Patient keine Hilfe mehr braucht
    Erkennt Aussagen wie "ich brauche keine Hilfe mehr", "das war alles", "danke, tschüss"

    patient_input: Die Eingabe des Patienten (optional, für Kontext)
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
                verabschiedung = f"Vielen Dank für Ihren Anruf, {patient_name}. Haben Sie einen schönen Tag! Auf Wiederhören."
            else:
                verabschiedung = f"Vielen Dank für Ihren Anruf, {patient_name}. Haben Sie einen schönen Abend! Auf Wiederhören."
        else:
            if 4 <= info['hour'] <= 17:
                verabschiedung = "Vielen Dank für Ihren Anruf. Haben Sie einen schönen Tag! Auf Wiederhören."
            else:
                verabschiedung = "Vielen Dank für Ihren Anruf. Haben Sie einen schönen Abend! Auf Wiederhören."

        # Notiz für das Gespräch
        call_manager.add_note(f"Gespräch beendet: {verabschiedung}")

        return verabschiedung

    except Exception as e:
        logging.error(f"Fehler bei Gesprächs-Beendigung: {e}")
        return "Vielen Dank für Ihren Anruf. Auf Wiederhören!"

@function_tool()
async def erkennung_gespraechsende_wunsch(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🔍 ERKENNUNG GESPRÄCHSENDE: Erkennt wenn Patient das Gespräch beenden möchte
    Beispiele: "ich brauche keine Hilfe mehr", "das war alles", "danke tschüss"

    patient_input: Die Eingabe des Patienten
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
            "danke tschüss",
            "danke tschuss",
            "auf wiederhören",
            "auf wiedersehen",
            "bis dann",
            "muss auflegen",
            "muss schluss machen",
            "keine weitere hilfe",
            "alles erledigt",
            "passt so",
            "ist gut so",
            "danke das reicht"
        ]

        # Prüfe ob Patient das Gespräch beenden möchte
        for muster in ende_muster:
            if muster in input_lower:
                # Gespräch beenden
                return await gespraech_hoeflich_beenden(context, patient_input)

        # Kein Gesprächsende erkannt - normale Antwort
        return await intelligente_antwort_mit_namen_erkennung(context, patient_input)

    except Exception as e:
        logging.error(f"Fehler bei Gesprächsende-Erkennung: {e}")
        return "Wie kann ich Ihnen weiter helfen?"

@function_tool()
async def intelligente_grund_nachfragen(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🤔 INTELLIGENTE GRUND-NACHFRAGEN: Fragt spezifisch nach dem Grund für den Termin
    - Wenn kein Grund angegeben: "Wieso benötigen Sie einen Termin?"
    - Bei "Kontrolle": "Gibt es einen besonderen Grund oder nur normale Untersuchung?"
    - Bei vagen Angaben: Spezifische Nachfragen

    patient_input: Die Eingabe des Patienten
    """
    try:
        input_lower = patient_input.lower()

        # 1. KEIN GRUND ERKANNT - Allgemeine Nachfrage
        if any(phrase in input_lower for phrase in [
            'brauche einen termin', 'möchte einen termin', 'termin vereinbaren',
            'termin buchen', 'kann ich einen termin'
        ]) and not any(grund in input_lower for grund in [
            'schmerz', 'weh', 'kontrolle', 'untersuchung', 'reinigung', 'implantat',
            'krone', 'füllung', 'zahnfleisch', 'weisheitszahn', 'bleaching', 'notfall'
        ]):
            return "Gerne vereinbare ich einen Termin für Sie. Wieso benötigen Sie denn einen Termin?"

        # 2. KONTROLLE/UNTERSUCHUNG - Spezifische Nachfrage
        elif any(word in input_lower for word in ['kontrolle', 'untersuchung', 'check', 'vorsorge']):
            return "Sie möchten zur Kontrolle kommen. Gibt es einen besonderen Grund oder ist es einfach eine normale Untersuchung?"

        # 3. REINIGUNG - Nachfrage nach Zusätzlichem
        elif any(word in input_lower for word in ['reinigung', 'zahnreinigung', 'prophylaxe']):
            return "Eine professionelle Zahnreinigung, sehr gut. Soll das mit einer Kontrolle kombiniert werden?"

        # 4. VAGE BEGRIFFE - Spezifische Nachfragen
        elif any(word in input_lower for word in ['problem', 'beschwerden', 'etwas', 'schauen']):
            return "Sie haben ein Problem. Was genau beschäftigt Sie denn?"

        # 5. BEREITS SPEZIFISCH - Verwende medizinische Nachfragen
        elif any(word in input_lower for word in [
            'schmerz', 'schmerzen', 'weh', 'implantat', 'krone', 'füllung',
            'weisheitszahn', 'zahnfleisch', 'blutet', 'geschwollen'
        ]):
            # Bereits spezifisch genug - verwende medizinische Nachfragen
            return await medizinische_nachfragen_stellen(context, patient_input)

        # 6. UNKLARE EINGABE - Höfliche Nachfrage
        else:
            return "Wieso benötigen Sie einen Termin?"

    except Exception as e:
        logging.error(f"Fehler bei Grund-Nachfragen: {e}")
        return "Wieso benötigen Sie einen Termin?"

@function_tool()
async def intelligente_grund_nachfragen(
    context: RunContext,
    patient_input: str
) -> str:
    """
    🤔 INTELLIGENTE GRUND-NACHFRAGEN: Fragt spezifisch nach dem Grund für den Termin
    - Wenn kein Grund angegeben: "Wofür benötigen Sie einen Termin?"
    - Bei "Kontrolle": "Gibt es einen besonderen Grund oder nur normale Untersuchung?"
    - Bei vagen Angaben: Spezifische Nachfragen

    patient_input: Die Eingabe des Patienten
    """
    try:
        input_lower = patient_input.lower()

        # 1. KEIN GRUND ERKANNT - Allgemeine Nachfrage
        if any(phrase in input_lower for phrase in [
            'brauche einen termin', 'möchte einen termin', 'termin vereinbaren',
            'termin buchen', 'appointment', 'kann ich einen termin'
        ]) and not any(grund in input_lower for grund in [
            'schmerz', 'weh', 'kontrolle', 'untersuchung', 'reinigung', 'implantat',
            'krone', 'füllung', 'zahnfleisch', 'weisheitszahn', 'bleaching', 'notfall'
        ]):
            return "Gerne vereinbare ich einen Termin für Sie. Wofür benötigen Sie denn den Termin? Haben Sie Beschwerden oder ist es für eine Kontrolle?"

        # 2. KONTROLLE/UNTERSUCHUNG - Spezifische Nachfrage
        elif any(word in input_lower for word in ['kontrolle', 'untersuchung', 'check', 'vorsorge']):
            return "Verstehe, Sie möchten zur Kontrolle kommen. Gibt es einen besonderen Grund oder Beschwerden, oder ist es einfach eine normale Vorsorgeuntersuchung?"

        # 3. REINIGUNG - Nachfrage nach Zusätzlichem
        elif any(word in input_lower for word in ['reinigung', 'zahnreinigung', 'prophylaxe']):
            return "Sehr gut, eine professionelle Zahnreinigung. Soll das mit einer Kontrolle kombiniert werden oder haben Sie zusätzliche Beschwerden?"

        # 4. VAGE BEGRIFFE - Spezifische Nachfragen
        elif any(word in input_lower for word in ['problem', 'beschwerden', 'etwas', 'schauen']):
            return "Ich verstehe, Sie haben ein Problem. Können Sie mir sagen, was genau Sie beschäftigt? Haben Sie Schmerzen oder geht es um etwas Bestimmtes?"

        # 5. ZAHNFLEISCH - Detaillierte Nachfrage
        elif any(word in input_lower for word in ['zahnfleisch', 'blutet', 'geschwollen']):
            return "Ach so, es geht um das Zahnfleisch. Blutet es beim Zähneputzen oder ist es geschwollen? Seit wann haben Sie das bemerkt?"

        # 6. ZAHN ALLGEMEIN - Spezifische Nachfrage
        elif any(word in input_lower for word in ['zahn', 'zähne']) and not any(word in input_lower for word in ['schmerz', 'weh']):
            return "Es geht um einen Zahn. Haben Sie Schmerzen oder ist etwas anderes mit dem Zahn? Ist er abgebrochen oder haben Sie andere Beschwerden?"

        # 7. ÄSTHETIK/AUSSEHEN - Beratungsansatz
        elif any(word in input_lower for word in ['schön', 'aussehen', 'ästhetik', 'weiß', 'gerade']):
            return "Sie interessieren sich für ästhetische Zahnbehandlung. Geht es um die Farbe der Zähne, die Stellung oder etwas anderes?"

        # 8. KINDER - Spezielle Nachfrage
        elif any(word in input_lower for word in ['kind', 'kinder', 'sohn', 'tochter']):
            return "Ah, es geht um ein Kind. Wie alt ist das Kind und gibt es bestimmte Beschwerden oder ist es der erste Zahnarztbesuch?"

        # 9. ANGST/NERVÖS - Einfühlsame Nachfrage
        elif any(word in input_lower for word in ['angst', 'nervös', 'furcht', 'scared']):
            return "Ich verstehe, dass Zahnarztbesuche manchmal Angst machen können. Wir nehmen uns gerne Zeit für Sie. Wofür benötigen Sie den Termin?"

        # 10. DRINGEND/SCHNELL - Notfall-Einschätzung
        elif any(word in input_lower for word in ['dringend', 'schnell', 'sofort', 'heute', 'morgen']):
            return "Das klingt dringend. Haben Sie Schmerzen oder was ist passiert? Je nach Situation können wir einen Notfalltermin arrangieren."

        # 11. BEREITS SPEZIFISCH - Keine weitere Nachfrage nötig
        elif any(word in input_lower for word in [
            'schmerz', 'schmerzen', 'weh', 'implantat', 'krone', 'füllung',
            'weisheitszahn', 'wurzelbehandlung', 'extraktion', 'bleaching'
        ]):
            # Bereits spezifisch genug - verwende medizinische Nachfragen
            return await medizinische_nachfragen_stellen(context, patient_input)

        # 12. UNKLARE EINGABE - Höfliche Nachfrage
        else:
            return "Gerne helfe ich Ihnen weiter. Können Sie mir sagen, wofür Sie einen Termin benötigen? Haben Sie Beschwerden oder geht es um eine Kontrolle?"

    except Exception as e:
        logging.error(f"Fehler bei Grund-Nachfragen: {e}")
        return "Gerne vereinbare ich einen Termin für Sie. Wofür benötigen Sie denn den Termin?"

@function_tool()
async def conversational_repair(
    context: RunContext,
    user_input: str
) -> str:
    """
    🧠 SMART FALLBACK: Conversational Repair für Korrekturen
    - Erkennt "Nein, lieber 11:30" und korrigiert letzten Terminvorschlag
    - Stateful Dialog ohne Neustart

    user_input: Korrektur-Eingabe des Patienten
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

                return f"Verstehe! Sie möchten lieber {corrected_slot['wochentag']}, {corrected_slot['datum']} um {corrected_slot['uhrzeit']} Uhr. Lassen Sie mich das für Sie prüfen."
            else:
                return "Entschuldigung, ich habe Ihre Korrektur nicht ganz verstanden. Können Sie mir sagen, wann Sie den Termin lieber hätten?"

        # Keine Korrektur erkannt
        return "Wie kann ich Ihnen weiter helfen?"

    except Exception as e:
        logging.error(f"Fehler bei Conversational Repair: {e}")
        return "Entschuldigung, können Sie das nochmal sagen?"
