import logging
from livekit.agents import function_tool, RunContext
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json
from clinic_knowledge import (
    CLINIC_INFO, SERVICES, FAQ, APPOINTMENT_TYPES, 
    INSURANCE_INFO, PAYMENT_OPTIONS, STAFF
)

# Simple in-memory storage for appointments (in production, use a proper database)
appointments_db = {}
patient_db = {}

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
