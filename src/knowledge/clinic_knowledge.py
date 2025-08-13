# Zahnarztpraxis Dr. Smith - Wissensdatenbank

CLINIC_INFO = {
    "name": "Zahnarztpraxis Dr. Smith",
    "address": "Hauptstraße 123, 10115 Berlin, Deutschland",
    "phone": "+49 30 12345678",
    "email": "info@praxis-weber.de",
    "website": "www.praxis-weber.de",
    "hours": {
        "montag": "8:00-18:00",
        "dienstag": "8:00-18:00", 
        "mittwoch": "8:00-18:00",
        "donnerstag": "8:00-18:00",
        "freitag": "8:00-16:00",
        "samstag": "9:00-13:00",
        "sonntag": "Geschlossen"
    },
    "emergency_hours": "Notfälle nach Terminvereinbarung auch außerhalb der Öffnungszeiten",
    "parking": "Kostenlose Parkplätze verfügbar",
    "accessibility": "Praxis ist rollstuhlgerecht"
}

SERVICES = {
    "allgemeine_zahnheilkunde": {
        "name": "Allgemeine Zahnheilkunde",
        "description": "Kontrolluntersuchungen, Diagnose und grundlegende Zahnbehandlungen",
        "duration": "30-60 Minuten",
        "price_range": "€50-150"
    },
    "zahnreinigung": {
        "name": "Professionelle Zahnreinigung",
        "description": "Professionelle Reinigung, Entfernung von Zahnstein und Plaque",
        "duration": "45 Minuten",
        "price_range": "€80-120"
    },
    "kieferorthopaedie": {
        "name": "orthodontics",
        "description": "Feste und herausnehmbare Zahnspangen, unsichtbare Aligner",
        "duration": "45-90 Minuten",
        "price_range": "€2000-6000 (komplette Behandlung)"
    },
    "implantologie": {
        "name": "Implantologie",
        "description": "Titan-Zahnimplantate zum Ersatz fehlender Zähne",
        "duration": "60-120 Minuten",
        "price_range": "€800-2500 pro Implantat"
    },
    "aesthetische_zahnheilkunde": {
        "name": "Ästhetische Zahnheilkunde",
        "description": "Bleaching, Veneers, ästhetische Rekonstruktionen",
        "duration": "60-90 Minuten",
        "price_range": "€200-800"
    },
    "endodontie": {
        "name": "endodontics",
        "description": "Wurzelkanalbehandlungen und Nervbehandlungen",
        "duration": "60-90 Minuten",
        "price_range": "€300-600"
    },
    "oralchirurgie": {
        "name": "Oralchirurgie",
        "description": "Zahnentfernungen, Weisheitszahn-Operationen",
        "duration": "30-60 Minuten",
        "price_range": "€100-400"
    },
    "prothetik": {
        "name": "Zahnprothetik",
        "description": "Feste und herausnehmbare Prothesen, Kronen und Brücken",
        "duration": "Mehrere Termine",
        "price_range": "€400-1500 pro Element"
    }
}

STAFF = {
    "dr_weber": {
        "name": "Dr. Smith",
        "title": "Zahnarzt",
        "specializations": ["Allgemeine Zahnheilkunde", "Ästhetische Zahnheilkunde", "Implantologie"],
        "experience": "15 Jahre Erfahrung",
        "languages": ["Deutsch", "Englisch"]
    },
    "prophylaxe_assistentin": {
        "name": "Frau Müller",
        "title": "Dentalhygienikerin",
        "specializations": ["dental cleaning", "Prophylaxe"],
        "experience": "8 Jahre Erfahrung"
    }
}

FAQ = {
    "kosten_kontrolluntersuchung": {
        "question": "Was kostet eine Kontrolluntersuchung?",
        "answer": "Eine Kontrolluntersuchung kostet €50-80. Der Preis kann je nach Komplexität der Untersuchung und eventuell notwendigen Röntgenaufnahmen variieren."
    },
    "krankenversicherung": {
        "question": "Nehmen Sie Krankenversicherungen an?",
        "answer": "Ja, wir akzeptieren alle gesetzlichen und privaten Krankenversicherungen. Bitte bringen Sie Ihre Versichertenkarte zum Termin mit."
    },
    "notfaelle": {
        "question": "Was tun bei einem Zahnnotfall?",
        "answer": "Bei Zahnnotfällen rufen Sie unsere Praxisnummer an. Wir bieten auch außerhalb der Öffnungszeiten Notfalltermine bei akuten Schmerzen oder Verletzungen an."
    },
    "erster_termin": {
        "question": "Was soll ich zum ersten Termin mitbringen?",
        "answer": "Bringen Sie bitte einen Ausweis, Ihre Versichertenkarte, eventuell vorhandene Röntgenbilder und eine Liste Ihrer Medikamente mit."
    },
    "zahlungsmethoden": {
        "question": "Welche Zahlungsmethoden akzeptieren Sie?",
        "answer": "Wir akzeptieren Bargeld, EC- und Kreditkarten, Überweisungen und bieten Ratenzahlung für teure Behandlungen an."
    },
    "kinder": {
        "question": "Behandeln Sie auch Kinder?",
        "answer": "Ja, wir bieten Kinderzahnheilkunde für Kinder ab 3 Jahren an. Wir schaffen eine freundliche und beruhigende Atmosphäre für unsere kleinen Patienten."
    },
    "betaeubung": {
        "question": "Verwenden Sie Betäubung bei Behandlungen?",
        "answer": "Ja, wir verwenden örtliche Betäubung für alle Behandlungen, die Schmerzen verursachen könnten. Für ängstliche Patienten bieten wir auch Sedierung an."
    },
    "zahnreinigung_haeufigkeit": {
        "question": "Wie oft sollte man eine Zahnreinigung machen lassen?",
        "answer": "Wir empfehlen eine professionelle Zahnreinigung alle 6 Monate, aber die Häufigkeit kann je nach individuellem Mundgesundheitszustand variieren."
    }
}

APPOINTMENT_TYPES = {
    "kontrolluntersuchung": {
        "name": "check-up",
        "duration": 30,
        "description": "Allgemeine Kontrolle des Mundgesundheitszustands"
    },
    "zahnreinigung": {
        "name": "Professionelle Zahnreinigung",
        "duration": 45,
        "description": "Professionelle Reinigung und Zahnstein-Entfernung"
    },
    "notfalltermin": {
        "name": "Notfalltermin",
        "duration": 30,
        "description": "Für akute Schmerzen oder Zahnnotfälle"
    },
    "kieferorthopaedie": {
        "name": "Kieferorthopädische Beratung",
        "duration": 60,
        "description": "Beratung für Zahnspangen oder Aligner"
    },
    "implantologie": {
        "name": "Implantologie-Beratung",
        "duration": 45,
        "description": "Beratung für Zahnimplantate"
    },
    "aesthetik": {
        "name": "Ästhetische Beratung",
        "duration": 45,
        "description": "Bleaching, Veneers und ästhetische Behandlungen"
    }
}

INSURANCE_INFO = {
    "accepted_insurances": [
        "AOK",
        "Techniker Krankenkasse",
        "Barmer",
        "DAK",
        "IKK",
        "Allianz Private",
        "DKV",
        "Signal Iduna"
    ],
    "coverage_info": "Die Kostenübernahme variiert je nach Versicherungsplan. Bitte prüfen Sie vor dem Termin Ihre Leistungsansprüche.",
    "direct_billing": "Direktabrechnung mit den meisten Versicherungen möglich. Verfügbarkeit bei Terminbuchung prüfen."
}

PAYMENT_OPTIONS = {
    "methods": ["Bargeld", "EC-Karte", "Kreditkarte", "Überweisung", "Ratenzahlung"],
    "installments": "Ratenzahlungspläne verfügbar für Behandlungen über €500",
    "receipts": "Wir stellen immer steuerlich absetzbare Behandlungsrechnungen aus"
}
