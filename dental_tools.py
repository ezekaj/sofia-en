import logging
from livekit.agents import function_tool, RunContext
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import json
from clinic_knowledge import (
    CLINIC_INFO, SERVICES, FAQ, APPOINTMENT_TYPES, 
    INSURANCE_INFO, PAYMENT_OPTIONS, STAFF
)
from appointment_manager import appointment_manager

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
        
    def add_note(self, note: str):
        self.notes.append(f"{datetime.now().strftime('%H:%M:%S')}: {note}")
        
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
        summary = f"Gespräch beendet um {datetime.now().strftime('%H:%M:%S')}\n"
        if self.patient_info:
            summary += f"Patient: {self.patient_info.get('name', 'N/A')}\n"
            summary += f"Telefon: {self.patient_info.get('phone', 'N/A')}\n"
        if self.scheduled_appointment:
            summary += f"Termin gebucht: {self.scheduled_appointment}\n"
        if self.notes:
            summary += f"Notizen: {', '.join(self.notes)}\n"
        return summary

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
Zahnarztpraxis Dr. Emanuela
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
Kontakt Zahnarztpraxis Dr. Emanuela:
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
        logging.error(f"Errore nel recupero informazioni clinica: {e}")
        return "Entschuldigung, es ist ein Fehler beim Abrufen der Informationen aufgetreten."

@function_tool()
async def get_services_info(
    context: RunContext,
    service_type: str = "all"
) -> str:
    """
    Fornisce informazioni sui servizi dentistici offerti.
    service_type può essere: 'all', 'odontoiatria_generale', 'igiene_dentale', 'ortodonzia', 'implantologia', 'estetica_dentale', 'endodonzia', 'chirurgia_orale', 'protesi'
    """
    try:
        if service_type == "all":
            services_text = "Servizi offerti dal nostro studio:\n\n"
            for key, service in SERVICES.items():
                services_text += f"• {service['name']}: {service['description']}\n"
                services_text += f"  Durata: {service['duration']}, Costo: {service['price_range']}\n\n"
            return services_text
        
        elif service_type in SERVICES:
            service = SERVICES[service_type]
            return f"""
{service['name']}
Descrizione: {service['description']}
Durata della seduta: {service['duration']}
Costo indicativo: {service['price_range']}
"""
        else:
            return "Servizio non trovato. I nostri servizi principali sono: odontoiatria generale, igiene dentale, ortodonzia, implantologia, estetica dentale, endodonzia, chirurgia orale e protesi."
            
    except Exception as e:
        logging.error(f"Errore nel recupero informazioni servizi: {e}")
        return "Mi dispiace, si è verificato un errore nel recupero delle informazioni sui servizi."

@function_tool()
async def answer_faq(
    context: RunContext,
    question_topic: str
) -> str:
    """
    Risponde alle domande frequenti sui servizi dentistici.
    question_topic può essere: 'costi', 'assicurazioni', 'emergenze', 'prima_visita', 'pagamenti', 'bambini', 'anestesia', 'igiene_frequenza'
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
        logging.error(f"Errore nel recupero FAQ: {e}")
        return "Mi dispiace, si è verificato un errore nel recupero delle informazioni."

@function_tool()
async def check_availability(
    context: RunContext,
    date: str,
    appointment_type: str = "visita_controllo"
) -> str:
    """
    Controlla la disponibilità per un appuntamento in una data specifica.
    date formato: YYYY-MM-DD
    appointment_type: tipo di appuntamento richiesto
    """
    try:
        # Simulazione controllo disponibilità (in produzione, integrare con sistema di calendario reale)
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Controlla se la data è nel passato
        if target_date.date() < datetime.now().date():
            return "Mi dispiace, non posso prenotare appuntamenti per date passate."
        
        # Controlla se è domenica (clinica chiusa)
        if target_date.weekday() == 6:  # Domenica
            return "Mi dispiace, la clinica è chiusa la domenica. Posso proporle un altro giorno?"
        
        # Controlla se è sabato (orario ridotto)
        if target_date.weekday() == 5:  # Sabato
            available_times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30"]
        else:
            available_times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", 
                             "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]
        
        # Simula alcuni slot già occupati
        occupied_slots = appointments_db.get(date, [])
        available_times = [time for time in available_times if time not in occupied_slots]
        
        if available_times:
            return f"Disponibilità per {date}:\nOrari disponibili: {', '.join(available_times[:6])}"
        else:
            # Proponi date alternative
            next_date = target_date + timedelta(days=1)
            return f"Mi dispiace, non ci sono slot disponibili per {date}. Posso proporle {next_date.strftime('%Y-%m-%d')}?"
            
    except ValueError:
        return "Formato data non valido. Utilizzare il formato YYYY-MM-DD (es. 2024-01-15)."
    except Exception as e:
        logging.error(f"Errore nel controllo disponibilità: {e}")
        return "Mi dispiace, si è verificato un errore nel controllo della disponibilità."

@function_tool()
async def schedule_appointment(
    context: RunContext,
    patient_name: str,
    phone: str,
    date: str,
    time: str,
    appointment_type: str = "visita_controllo",
    notes: str = ""
) -> str:
    """
    Prenota un nuovo appuntamento.
    Parametri: nome paziente, telefono, data (YYYY-MM-DD), ora (HH:MM), tipo appuntamento, note aggiuntive
    """
    try:
        # Validazione data e ora
        appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        if appointment_datetime < datetime.now():
            return "Non posso prenotare appuntamenti per date e orari passati."
        
        # Controlla se il tipo di appuntamento esiste
        if appointment_type not in APPOINTMENT_TYPES:
            return f"Tipo di appuntamento non riconosciuto. Tipi disponibili: {', '.join(APPOINTMENT_TYPES.keys())}"
        
        # Simula la prenotazione (in produzione, salvare in database)
        appointment_id = f"APP_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
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
        
        # Salva l'appuntamento
        if date not in appointments_db:
            appointments_db[date] = []
        appointments_db[date].append(time)
        
        # Salva i dati del paziente
        patient_db[phone] = {
            "name": patient_name,
            "phone": phone,
            "last_appointment": appointment_id
        }
        
        appointment_info = APPOINTMENT_TYPES[appointment_type]
        
        return f"""
Appuntamento confermato!

Dettagli:
• Paziente: {patient_name}
• Data: {date}
• Ora: {time}
• Tipo: {appointment_info['name']}
• Durata prevista: {appointment_info['duration']} minuti
• Codice prenotazione: {appointment_id}

La contatteremo il giorno prima per confermare l'appuntamento.
Ricordi di portare un documento d'identità e la tessera sanitaria.
"""
        
    except ValueError:
        return "Formato data o ora non valido. Utilizzare YYYY-MM-DD per la data e HH:MM per l'ora."
    except Exception as e:
        logging.error(f"Errore nella prenotazione: {e}")
        return "Mi dispiace, si è verificato un errore durante la prenotazione. La prego di riprovare."

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
    Raccoglie le informazioni del paziente per la prima visita.
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
        
        # Salva i dati del paziente
        patient_db[phone] = patient_data
        
        return f"""
Informazioni paziente registrate:
• Nome: {name}
• Telefono: {phone}
• Email: {email if email else 'Non fornita'}

Grazie per aver fornito le sue informazioni. 
Alla prima visita le chiederemo di compilare una scheda anamnestica più dettagliata.
Ricordi di portare un documento d'identità, tessera sanitaria ed eventuali radiografie precedenti.
"""
        
    except Exception as e:
        logging.error(f"Errore nella raccolta dati paziente: {e}")
        return "Mi dispiace, si è verificato un errore nel salvataggio delle informazioni."

@function_tool()
async def cancel_appointment(
    context: RunContext,
    patient_name: str,
    phone: str,
    date: str,
    time: str = ""
) -> str:
    """
    Cancella un appuntamento esistente.
    Parametri: nome paziente, telefono, data (YYYY-MM-DD), ora (opzionale)
    """
    try:
        # Cerca l'appuntamento
        if date in appointments_db:
            if time and time in appointments_db[date]:
                appointments_db[date].remove(time)
                return f"""
Appuntamento cancellato con successo.

Dettagli cancellazione:
• Paziente: {patient_name}
• Data: {date}
• Ora: {time}

La cancellazione è stata registrata. Se desidera riprogrammare, sarò felice di aiutarla a trovare una nuova data.
"""
            elif not time:
                # Se non è specificata l'ora, mostra gli appuntamenti per quella data
                return f"Ho trovato appuntamenti per {date}. Può specificare l'orario da cancellare?"

        return f"Non ho trovato appuntamenti per {patient_name} in data {date}. Può verificare i dati?"

    except Exception as e:
        logging.error(f"Errore nella cancellazione: {e}")
        return "Mi dispiace, si è verificato un errore durante la cancellazione."

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
    Riprogramma un appuntamento esistente.
    Parametri: nome, telefono, vecchia data, vecchia ora, nuova data, nuova ora
    """
    try:
        # Verifica che il vecchio appuntamento esista
        if old_date not in appointments_db or old_time not in appointments_db[old_date]:
            return f"Non ho trovato l'appuntamento originale per {patient_name} il {old_date} alle {old_time}."

        # Verifica disponibilità della nuova data/ora
        new_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
        if new_datetime < datetime.now():
            return "Non posso riprogrammare per date e orari passati."

        # Controlla se il nuovo slot è disponibile
        if new_date in appointments_db and new_time in appointments_db[new_date]:
            return f"Mi dispiace, lo slot {new_date} alle {new_time} è già occupato. Posso proporle altri orari?"

        # Esegui la riprogrammazione
        # Rimuovi il vecchio appuntamento
        appointments_db[old_date].remove(old_time)

        # Aggiungi il nuovo appuntamento
        if new_date not in appointments_db:
            appointments_db[new_date] = []
        appointments_db[new_date].append(new_time)

        return f"""
Appuntamento riprogrammato con successo!

Vecchio appuntamento:
• Data: {old_date}
• Ora: {old_time}

Nuovo appuntamento:
• Paziente: {patient_name}
• Data: {new_date}
• Ora: {new_time}

La contatteremo il giorno prima per confermare il nuovo appuntamento.
"""

    except ValueError:
        return "Formato data o ora non valido. Utilizzare YYYY-MM-DD per la data e HH:MM per l'ora."
    except Exception as e:
        logging.error(f"Errore nella riprogrammazione: {e}")
        return "Mi dispiace, si è verificato un errore durante la riprogrammazione."

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

Le consiglio di contattare la sua assicurazione per verificare la copertura specifica del trattamento di cui necessita.
"""
            else:
                return f"""
{insurance_name} non è nell'elenco delle nostre assicurazioni convenzionate.

Assicurazioni accettate:
{', '.join(INSURANCE_INFO["accepted_insurances"])}

Tuttavia, può sempre verificare con la sua assicurazione se offre rimborsi per le nostre prestazioni.
"""
        else:
            return f"""
Assicurazioni sanitarie accettate:
{', '.join(INSURANCE_INFO["accepted_insurances"])}

{INSURANCE_INFO["coverage_info"]}
{INSURANCE_INFO["direct_billing"]}
"""

    except Exception as e:
        logging.error(f"Errore info assicurazioni: {e}")
        return "Mi dispiace, si è verificato un errore nel recupero delle informazioni assicurative."

@function_tool()
async def get_payment_info(
    context: RunContext
) -> str:
    """
    Fornisce informazioni sui metodi di pagamento accettati.
    """
    try:
        return f"""
Metodi di pagamento accettati:
{', '.join(PAYMENT_OPTIONS["methods"])}

{PAYMENT_OPTIONS["installments"]}

{PAYMENT_OPTIONS["receipts"]}

Per trattamenti costosi, possiamo discutere piani di pagamento personalizzati durante la visita.
"""

    except Exception as e:
        logging.error(f"Errore info pagamenti: {e}")
        return "Mi dispiace, si è verificato un errore nel recupero delle informazioni sui pagamenti."

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
            ab_datum = datetime.now().strftime("%Y-%m-%d")
        
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
async def termine_suchen(
    context: RunContext,
    suchbegriff: str,
    zeitraum: str = "naechste_woche"
) -> str:
    """
    Sucht nach Terminen basierend auf verschiedenen Kriterien.
    suchbegriff: Suchbegriff (Patientenname, Telefon, Behandlungsart)
    zeitraum: Zeitraum (heute, morgen, naechste_woche, naechster_monat)
    """
    try:
        return appointment_manager.termin_suchen(suchbegriff, zeitraum)
        
    except Exception as e:
        logging.error(f"Fehler bei der Terminsuche: {e}")
        return "Entschuldigung, es gab ein Problem bei der Terminsuche."

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
                return f"✅ Der Termin am {datum} um {uhrzeit} ist verfügbar!"
            else:
                return f"❌ Der Termin am {datum} um {uhrzeit} ist bereits belegt."
        else:
            # Zeige alle verfügbaren Zeiten für den Tag
            verfuegbare_zeiten = appointment_manager.get_verfuegbare_termine_tag(datum)
            if verfuegbare_zeiten:
                return f"✅ Verfügbare Zeiten am {datum}:\n" + "\n".join(f"• {zeit}" for zeit in verfuegbare_zeiten)
            else:
                return f"❌ Am {datum} sind keine Termine verfügbar."
        
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
    Gibt aktuelle Datum- und Zeitinformationen zurück, die die KI bereits kennt.
    Zeigt Praxiszeiten, Wochentag und Verfügbarkeit.
    """
    try:
        info = appointment_manager.get_current_datetime_info()
        
        antwort = f"🕐 **Aktuelle Datum- und Zeitinformationen:**\n\n"
        antwort += f"📅 **Heute**: {info['wochentag']}, {info['formatiert']}\n"
        antwort += f"📆 **Datum**: {info['aktuelles_datum']}\n"
        antwort += f"🕐 **Uhrzeit**: {info['aktuelle_uhrzeit']}\n\n"
        
        antwort += f"🏥 **Praxisstatus:**\n"
        if info['ist_heute_arbeitstag']:
            antwort += f"✅ Heute ist ein Arbeitstag\n"
            arbeitszeiten = info['arbeitszeiten_heute']
            antwort += f"⏰ Öffnungszeiten heute: {arbeitszeiten['vormittag']}"
            if arbeitszeiten['nachmittag']:
                antwort += f", {arbeitszeiten['nachmittag']}"
            antwort += "\n"
            
            if info['praxis_offen']:
                antwort += f"🟢 Praxis ist derzeit **GEÖFFNET**\n"
            else:
                antwort += f"🔴 Praxis ist derzeit **GESCHLOSSEN**\n"
        else:
            antwort += f"❌ Heute ist kein Arbeitstag (Sonntag)\n"
            antwort += f"🔴 Praxis ist **GESCHLOSSEN**\n"
        
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
            
            return f"✅ **Termin erfolgreich gebucht!**\n\n" \
                   f"👤 **Patient**: {patient_name}\n" \
                   f"📞 **Telefon**: {phone}\n" \
                   f"📅 **Datum**: {appointment_date}\n" \
                   f"🕐 **Uhrzeit**: {appointment_time}\n" \
                   f"🦷 **Behandlung**: {treatment_type}\n" \
                   f"📝 **Notizen**: {notes if notes else 'Keine'}\n\n" \
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
            return f"✅ **Termin verfügbar!**\n\n" \
                   f"📅 **Datum**: {datum}\n" \
                   f"🕐 **Uhrzeit**: {uhrzeit}\n" \
                   f"🦷 **Behandlung**: {behandlungsart}\n\n" \
                   f"Möchten Sie diesen Termin buchen? Ich benötige dann Ihren Namen und Ihre Telefonnummer."
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
        # Gespräch als beendet markieren - SOFORT!
        call_manager.initiate_call_end()
        call_manager.status = CallStatus.COMPLETED
        call_manager.add_note(f"Gespräch beendet: {grund}")
        
        # SEHR KURZE Abschiedsnachricht - keine langen Texte!
        response = f"Auf Wiedersehen! Vielen Dank für Ihren Anruf."
        
        # Falls ein Termin gebucht wurde, kurze Bestätigung
        if call_manager.scheduled_appointment:
            apt = call_manager.scheduled_appointment
            response += f"\n✅ Ihr Termin: {apt['date']} um {apt['time']}"
            
        # Log für Debugging
        logging.info(f"🔴 GESPRÄCH BEENDET SOFORT: {grund}")
        
        # Ende-Signal SOFORT hinzufügen
        response += f"\n*[CALL_END_SIGNAL]*"
        logging.info("📞 Ende-Signal hinzugefügt - GESPRÄCH BEENDET")
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler beim Beenden des Gesprächs: {e}")
        call_manager.initiate_call_end()
        call_manager.status = CallStatus.COMPLETED
        return f"Auf Wiedersehen!\n*[CALL_END_SIGNAL]*"

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
    Erstellt eine zeitbewusste Begrüßung basierend auf der aktuellen Uhrzeit.
    """
    try:
        current_time = datetime.now()
        hour = current_time.hour
        
        # Bestimme die passende Begrüßung basierend auf der Uhrzeit
        if 6 <= hour < 12:
            begruessung = "Guten Morgen"
        elif 12 <= hour < 18:
            begruessung = "Guten Tag"
        else:
            begruessung = "Guten Abend"
        
        # Erweiterte Begrüßung mit Praxisinfo
        response = f"{begruessung}! Ich bin Sofia, Ihre Assistentin bei der Zahnarztpraxis Dr. Emanuela. "
        response += f"Es ist {current_time.strftime('%H:%M')} Uhr. "
        
        # Praxisstatus hinzufügen
        datetime_info = appointment_manager.get_current_datetime_info()
        if datetime_info['praxis_offen']:
            response += "Unsere Praxis ist derzeit geöffnet. "
        else:
            response += "Unsere Praxis ist derzeit geschlossen. "
            
        response += "Wie kann ich Ihnen heute helfen?"
        
        # Notiz hinzufügen
        call_manager.add_note(f"Begrüßung: {begruessung} um {current_time.strftime('%H:%M')} Uhr")
        
        return response
        
    except Exception as e:
        logging.error(f"Fehler bei zeitbewusster Begrüßung: {e}")
        return "Guten Tag! Ich bin Sofia, Ihre Assistentin bei der Zahnarztpraxis Dr. Emanuela. Wie kann ich Ihnen helfen?"

@function_tool()
async def get_zeitabhaengige_begruessung(
    context: RunContext
) -> str:
    """
    Gibt eine zeitabhängige Begrüßung basierend auf der aktuellen Uhrzeit zurück.
    04:00-10:30 = Guten Morgen
    10:31-17:59 = Guten Tag  
    18:00-03:59 = Guten Abend
    """
    try:
        # Aktuelle Zeit abrufen
        jetzt = datetime.now()
        stunde = jetzt.hour
        minute = jetzt.minute
        
        # Zeitabhängige Begrüßung bestimmen
        if stunde >= 4 and (stunde < 10 or (stunde == 10 and minute <= 30)):
            begruessung = "Guten Morgen"
            tageszeit = "morgens"
        elif (stunde == 10 and minute > 30) or (stunde >= 11 and stunde < 18):
            begruessung = "Guten Tag"
            tageszeit = "tagsüber"
        else:  # 18:00-03:59
            begruessung = "Guten Abend"
            tageszeit = "abends"
            
        # Formatierte Zeit
        zeit_formatiert = jetzt.strftime("%H:%M")
        datum_formatiert = jetzt.strftime("%A, %d.%m.%Y")
        
        # Deutsche Wochentage
        wochentage = {
            'Monday': 'Montag',
            'Tuesday': 'Dienstag', 
            'Wednesday': 'Mittwoch',
            'Thursday': 'Donnerstag',
            'Friday': 'Freitag',
            'Saturday': 'Samstag',
            'Sunday': 'Sonntag'
        }
        
        englischer_tag = jetzt.strftime("%A")
        deutscher_tag = wochentage.get(englischer_tag, englischer_tag)
        datum_deutsch = jetzt.strftime(f"{deutscher_tag}, %d.%m.%Y")
        
        antwort = f"🕐 **Zeitabhängige Begrüßung:**\n\n"
        antwort += f"**{begruessung}!** 👋\n\n"
        antwort += f" **Sofia hier, Ihre Praxisassistentin!**\n"
        antwort += f"Wie kann ich Ihnen helfen?\n\n"
        
        # KEINE Öffnungszeiten am Anfang erwähnen - nur bei konkreten Fragen
        
        return antwort
        
    except Exception as e:
        logging.error(f"Fehler bei zeitabhängiger Begrüßung: {e}")
        return "Guten Tag! Ich bin Sofia, Ihre Praxisassistentin. Wie kann ich Ihnen helfen?"

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
    Patient gibt Daten nur EINMAL ein und Termin wird sofort gebucht.
    """
    try:
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
        
        if result:
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
            
            return f"✅ **Perfekt! Ihr Termin ist gebucht!**\n\n" \
                   f"👤 **Name**: {patient_name}\n" \
                   f"📞 **Telefon**: {phone}\n" \
                   f"📅 **Termin**: {appointment_date} um {appointment_time}\n" \
                   f"🦷 **Behandlung**: {treatment_type}\n" \
                   f"📝 **Notizen**: {notes if notes else 'Keine besonderen Notizen'}\n\n" \
                   f"🎉 **Ihr Termin ist bestätigt!** Wir freuen uns auf Sie!\n" \
                   f"📞 Bei Fragen erreichen Sie uns unter: 0123 456 789"
        else:
            return f"❌ **Terminbuchung fehlgeschlagen**: Unbekannter Fehler beim Speichern"
            
    except Exception as e:
        logging.error(f"Fehler bei direkter Terminbuchung: {e}")
        return f"❌ Entschuldigung, es gab ein Problem bei der Terminbuchung: {str(e)}"
