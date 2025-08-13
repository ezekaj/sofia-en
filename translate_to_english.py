#!/usr/bin/env python3
"""
Translation script to convert German dental tools to English
"""

import re
import os

# Translation mappings for function names
FUNCTION_NAME_TRANSLATIONS = {
    # Original German -> English
    'get_naechste_freie_termine': 'get_next_available_appointments',
    'get_tagesplan_arzt': 'get_doctor_daily_schedule',
    'get_wochenuebersicht_arzt': 'get_doctor_weekly_overview',
    'termin_buchen_erweitert': 'book_appointment_extended',
    'get_patientenhistorie': 'get_patient_history',
    'termine_suchen_praxis': 'search_practice_appointments',
    'meine_termine_finden': 'find_my_appointments',
    'medizinische_nachfragen_stellen': 'ask_medical_followup_questions',
    'intelligente_terminbuchung_mit_nachfragen': 'smart_appointment_booking_with_followups',
    'namen_erkennen_und_speichern': 'recognize_and_save_name',
    'intelligente_antwort_mit_namen_erkennung': 'smart_response_with_name_recognition',
    'gespraech_hoeflich_beenden': 'end_conversation_politely',
    'erkennung_gespraechsende_wunsch': 'detect_conversation_end_wish',
    'intelligente_grund_nachfragen': 'smart_reason_followup',
    'get_praxis_statistiken': 'get_practice_statistics',
    'termin_absagen': 'cancel_appointment_by_id',
    'check_verfuegbarkeit_erweitert': 'check_availability_extended',
    'parse_terminwunsch': 'parse_appointment_request',
    'get_aktuelle_datetime_info': 'get_current_datetime_info',
    'get_intelligente_terminvorschlaege': 'get_smart_appointment_suggestions',
    'termin_buchen_mit_details': 'book_appointment_with_details',
    'termin_direkt_buchen': 'book_appointment_directly',
    'check_verfuegbarkeit_spezifisch': 'check_specific_availability',
    'gespraech_beenden': 'end_conversation',
    'notiz_hinzufuegen': 'add_note',
    'gespraech_status': 'conversation_status',
    'get_zeitabhaengige_begruessung': 'get_time_based_greeting',
    'get_zeitbewusste_begruessung': 'get_time_aware_greeting',
    'sofia_naechster_freier_termin': 'sofia_next_available_appointment',
    'sofia_termin_an_bestimmtem_tag': 'sofia_appointment_on_specific_day',
    'sofia_terminvorschlaege_intelligent': 'sofia_smart_appointment_suggestions',
    'sofia_heutige_termine_abrufen': 'sofia_get_todays_appointments',
    'sofia_meine_termine_finden_erweitert': 'sofia_find_my_appointments_extended',
    'termin_buchen_calendar_system': 'book_appointment_calendar_system',
    'terminbuchung_schritt_fuer_schritt': 'appointment_booking_step_by_step',
    'notfall_priorisierung': 'emergency_prioritization',
    'wartezeit_schaetzung': 'waiting_time_estimation',
    'termin_erinnerung_planen': 'schedule_appointment_reminder',
    'rezept_erneuern': 'renew_prescription',
    'behandlungsplan_status': 'treatment_plan_status',
    'lernfaehigkeit_analysieren': 'analyze_learning_capability',
    'haeufige_frage_beantworten': 'answer_frequent_question',
    'haeufige_behandlungsgruende': 'common_treatment_reasons',
}

# Key German phrases to translate
GERMAN_TO_ENGLISH = {
    # Days of the week
    'Montag': 'Monday',
    'Dienstag': 'Tuesday',
    'Mittwoch': 'Wednesday',
    'Donnerstag': 'Thursday',
    'Freitag': 'Friday',
    'Samstag': 'Saturday',
    'Sonntag': 'Sunday',
    
    # Months
    'Januar': 'January',
    'Februar': 'February',
    'März': 'March',
    'April': 'April',
    'Mai': 'May',
    'Juni': 'June',
    'Juli': 'July',
    'August': 'August',
    'September': 'September',
    'Oktober': 'October',
    'November': 'November',
    'Dezember': 'December',
    
    # Time-related
    'heute': 'today',
    'morgen': 'tomorrow',
    'gestern': 'yesterday',
    'Uhr': "o'clock",
    'vormittag': 'morning',
    'nachmittag': 'afternoon',
    'abend': 'evening',
    
    # Greetings
    'Guten Morgen': 'Good morning',
    'Guten Tag': 'Good day',
    'Guten Abend': 'Good evening',
    'Auf Wiedersehen': 'Goodbye',
    'Auf Wiederhören': 'Goodbye',
    'Tschüss': 'Bye',
    'Hallo': 'Hello',
    
    # Medical terms
    'Termin': 'appointment',
    'Termine': 'appointments',
    'Kontrolluntersuchung': 'check-up',
    'Zahnreinigung': 'dental cleaning',
    'Zahnhygiene': 'dental hygiene',
    'Füllung': 'filling',
    'Extraktion': 'extraction',
    'Zahnimplantat': 'dental implant',
    'Kieferorthopädie': 'orthodontics',
    'Zahnspange': 'braces',
    'Zahnersatz': 'dental prosthetics',
    'Endodontie': 'endodontics',
    'Wurzelbehandlung': 'root canal',
    'Zahnaufhellung': 'teeth whitening',
    'Zahnschmerzen': 'toothache',
    'Schmerzen': 'pain',
    
    # Practice related
    'Zahnarztpraxis': 'Dental Practice',
    'Praxis': 'practice',
    'Öffnungszeiten': 'opening hours',
    'geschlossen': 'closed',
    'geöffnet': 'open',
    
    # Common responses
    'Entschuldigung': 'Sorry',
    'Bitte': 'Please',
    'Danke': 'Thank you',
    'Vielen Dank': 'Thank you very much',
    'Gerne': 'Gladly',
    'Natürlich': 'Of course',
    
    # Doctor/Patient
    'Arzt': 'doctor',
    'Patient': 'patient',
    'Patienten': 'patients',
    
    # Emergency
    'Notfall': 'emergency',
    'Notfälle': 'emergencies',
    'dringend': 'urgent',
}

def translate_dental_tools():
    """Translate the dental_tools.py file from German to English"""
    
    input_file = 'src/dental/dental_tools.py'
    output_file = 'src/dental/dental_tools.py'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace function names
    for old_name, new_name in FUNCTION_NAME_TRANSLATIONS.items():
        # Replace in function definitions
        content = re.sub(f'async def {old_name}\\(', f'async def {new_name}(', content)
        # Replace in function calls
        content = re.sub(f'{old_name}\\(', f'{new_name}(', content)
        # Replace in imports and references
        content = re.sub(f'\\b{old_name}\\b', new_name, content)
    
    # Replace German text with English
    for german, english in GERMAN_TO_ENGLISH.items():
        # Replace in strings (both single and double quotes)
        content = re.sub(f'"{german}"', f'"{english}"', content)
        content = re.sub(f"'{german}'", f"'{english}'", content)
        # Replace in f-strings and text
        content = re.sub(f'\\b{german}\\b', english, content, flags=re.IGNORECASE)
    
    # Update specific German error messages
    content = content.replace(
        'Entschuldigung, es gab ein Fehler',
        'Sorry, there was an error'
    )
    content = content.replace(
        'Entschuldigung, es gab ein Problem',
        'Sorry, there was a problem'
    )
    
    # Update clinic info
    content = content.replace("'Zahnarztpraxis Dr. Weber'", "'Dr. Smith\\'s Dental Practice'")
    content = content.replace("'Musterstraße 123, 12345 Berlin'", "'123 Main Street, London SW1A 1AA'")
    content = content.replace("'030 12345678'", "'+44 20 7123 4567'")
    content = content.replace("'info@zahnarzt-weber.de'", "'info@drsmith-dental.co.uk'")
    content = content.replace("'www.zahnarzt-weber.de'", "'www.drsmith-dental.co.uk'")
    
    # Update fuzzy times to English
    fuzzy_times_english = '''# 🚀 PERFORMANCE BOOST: Fuzzy Times for vague time specifications
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
}'''
    
    # Replace the German fuzzy times section
    content = re.sub(
        r'# 🚀 PERFORMANCE BOOST:.*?FUZZY_TIMES = \{.*?\}',
        fuzzy_times_english,
        content,
        flags=re.DOTALL
    )
    
    # Write the translated content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Translated dental_tools.py to English")

def translate_agent_py():
    """Translate the agent.py file"""
    
    input_file = 'agent.py'
    output_file = 'agent.py'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update imports to use English function names
    for old_name, new_name in FUNCTION_NAME_TRANSLATIONS.items():
        content = re.sub(f'\\b{old_name}\\b', new_name, content)
    
    # Update language settings
    content = content.replace('language="de-DE"', 'language="en-US"')
    content = content.replace('voice="Aoede"', 'voice="Sage"')  # English voice
    
    # Update German text in logging messages
    for german, english in GERMAN_TO_ENGLISH.items():
        content = re.sub(f'"{german}"', f'"{english}"', content)
        content = re.sub(f"'{german}'", f"'{english}'", content)
    
    # Write the translated content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Translated agent.py to English")

def translate_clinic_knowledge():
    """Translate the clinic_knowledge.py file"""
    
    input_file = 'src/knowledge/clinic_knowledge.py'
    
    if os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Translate all German text
        for german, english in GERMAN_TO_ENGLISH.items():
            content = re.sub(f'"{german}"', f'"{english}"', content)
            content = re.sub(f"'{german}'", f"'{english}'", content)
        
        # Update clinic name
        content = content.replace("Dr. Weber", "Dr. Smith")
        
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Translated clinic_knowledge.py to English")

def main():
    """Main translation function"""
    print("Starting translation to English...")
    
    # Change to the elo-english directory
    os.chdir('C:\\Users\\User\\OneDrive\\Desktop\\elo-elvi\\elo-english')
    
    # Translate main files
    translate_dental_tools()
    translate_agent_py()
    translate_clinic_knowledge()
    
    print("Translation complete!")

if __name__ == "__main__":
    main()