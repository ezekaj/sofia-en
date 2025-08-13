# Deutsche zahnärztliche Terminologie und Trainingsdaten für Emanuela's Zahnarztpraxis

GERMAN_DENTAL_TERMINOLOGY = {
    # Grundlegende zahnärztliche Begriffe
    "zahn": "tooth",
    "zähne": "teeth", 
    "mund": "mouth",
    "zahnfleisch": "gums",
    "zunge": "tongue",
    "kiefer": "jaw",
    "unterkiefer": "lower jaw",
    "gaumen": "palate",
    "speichel": "saliva",
    
    # Zahnärztliche Behandlungen
    "reinigung": "cleaning",
    "zahnhygiene": "dental hygiene",
    "füllung": "filling",
    "extraktion": "extraction",
    "wurzelbehandlung": "root canal",
    "endodontie": "endodontics",
    "implantat": "implant",
    "prothese": "prosthesis",
    "krone": "crown",
    "brücke": "bridge",
    "zahnspange": "braces",
    "kieferorthopädie": "orthodontics",
    "bleaching": "whitening",
    "zahnsteinentfernung": "scaling",
    "versiegelung": "sealant",
    
    # Zahnprobleme
    "karies": "cavity",
    "zahnschmerzen": "toothache",
    "schmerzen": "pain",
    "schwellung": "swelling",
    "blutung": "bleeding",
    "empfindlichkeit": "sensitivity",
    "infektion": "infection",
    "abszess": "abscess",
    "zahnstein": "tartar",
    "plaque": "plaque",
    "mundgeruch": "bad breath",
    
    # Terminarten
    "besuch": "visit",
    "kontrolle": "check-up",
    "notfall": "emergency",
    "dringlichkeit": "urgency",
    "beratung": "consultation",
    "erste_untersuchung": "first examination",
    "nachkontrolle": "follow-up",
    "routinetermin": "routine appointment",
    
    # Zahnärztliche Instrumente
    "bohrer": "drill",
    "sonde": "probe",
    "spiegel": "mirror",
    "zange": "forceps",
    "skaler": "scaler",
    "röntgengerät": "x-ray machine",
    
    # Häufige Patientenaussagen auf Deutsch
    "patient_concerns": [
        "Ich habe Zahnschmerzen",
        "Mein Zahn tut weh",
        "Ich brauche eine Kontrolle",
        "Ich habe einen Notfall",
        "Wann kann ich einen Termin bekommen?",
        "Was kostet die Behandlung?",
        "Übernimmt das meine Versicherung?",
        "Ich habe Angst vor dem Zahnarzt",
        "Ich brauche eine Reinigung",
        "Mein Zahnfleisch blutet"
    ],
    
    # Übliche Antworten der Rezeption
    "receptionist_responses": [
        "Gerne vereinbare ich einen Termin für Sie",
        "Wann passt es Ihnen am besten?",
        "Ich schaue nach verfügbaren Terminen",
        "Das tut mir leid zu hören",
        "Lassen Sie mich das für Sie prüfen",
        "Ich helfe Ihnen gerne weiter",
        "Kann ich Ihre Daten aufnehmen?",
        "Haben Sie Ihre Versichertenkarte dabei?",
        "Welche Art von Behandlung benötigen Sie?",
        "Ist das ein Notfall?"
    ]
}

# Deutsche Zeitausdrücke für Termine
GERMAN_TIME_EXPRESSIONS = {
    "days": [
        "heute", "morgen", "übermorgen", 
        "montag", "dienstag", "mittwoch", "donnerstag", "freitag",
        "nächste woche", "übernächste woche"
    ],
    
    "times": [
        "vormittag", "nachmittag", "früh am morgen", "spät nachmittag",
        "acht uhr", "neun uhr", "zehn uhr", "elf uhr",
        "zwölf uhr", "dreizehn uhr", "vierzehn uhr", "fünfzehn uhr",
        "sechzehn uhr", "siebzehn uhr", "achtzehn uhr"
    ],
    
    "urgency": [
        "so schnell wie möglich", "dringend", "notfall", "heute noch",
        "am liebsten morgen", "diese woche noch", "baldmöglichst"
    ]
}

# Deutsche Höflichkeitsformen
GERMAN_POLITENESS = {
    "formal_greeting": [
        "Guten Tag", "Guten Morgen", "Guten Abend",
        "Sehr geehrte Damen und Herren"
    ],
    
    "informal_greeting": [
        "Hallo", "Hi", "Guten Tag"
    ],
    
    "closing": [
        "Auf Wiedersehen", "Vielen Dank", "Schönen Tag noch",
        "Bis bald", "Tschüss"
    ],
    
    "please_thank_you": [
        "bitte", "danke", "vielen dank", "bitte schön",
        "gern geschehen", "keine ursache"
    ]
}

# Häufige deutsche Dialoge in der Zahnarztpraxis
COMMON_GERMAN_CONVERSATIONS = [
    {
        "patient": "Hallo, ich hätte gerne einen Termin beim Zahnarzt.",
        "receptionist": "Guten Tag! Gerne vereinbare ich einen Termin für Sie. Für welche Art von Behandlung?"
    },
    {
        "patient": "Ich habe starke Zahnschmerzen.",
        "receptionist": "Das tut mir leid zu hören. Das klingt nach einem Notfall. Ich schaue, was wir heute noch machen können."
    },
    {
        "patient": "Was kostet eine Zahnreinigung?",
        "receptionist": "Ich gebe Ihnen gerne die Preise für unsere Prophylaxe-Behandlungen. Sind Sie privat oder gesetzlich versichert?"
    },
    {
        "patient": "Ich möchte meinen Termin verschieben.",
        "receptionist": "Kein Problem. Können Sie mir sagen, wann Ihr aktueller Termin ist, damit ich ihn finde?"
    },
    {
        "patient": "Übernimmt meine Krankenkasse die Kosten?",
        "receptionist": "Das hängt von der Behandlung und Ihrer Versicherung ab. Welche Krankenkasse haben Sie denn?"
    }
]

# Deutsche Notfall-Phrasen
GERMAN_EMERGENCY_PHRASES = [
    "Das ist ein Notfall",
    "Ich habe sehr starke Schmerzen",
    "Mein Zahn ist abgebrochen",
    "Ich blute stark",
    "Die Schwellung wird immer größer",
    "Ich kann nicht mehr kauen",
    "Die Schmerzen sind unerträglich",
    "Können Sie mir sofort helfen?"
]

# Deutsche Versicherungsterminologie
GERMAN_INSURANCE_TERMS = {
    "types": [
        "gesetzliche krankenversicherung", "private krankenversicherung",
        "beihilfe", "zusatzversicherung", "selbstzahler"
    ],
    
    "common_insurers": [
        "AOK", "Barmer", "TK", "DAK", "IKK", "BKK",
        "Allianz", "AXA", "DKV", "Signal Iduna"
    ],
    
    "coverage_terms": [
        "kassenleistung", "privatleistung", "zuzahlung", "eigenanteil",
        "kostenvoranschlag", "heil- und kostenplan"
    ]
}

# Deutsche Behandlungsterminologie
GERMAN_TREATMENT_TERMS = {
    "preventive": [
        "prophylaxe", "zahnreinigung", "fluoridierung", 
        "versiegelung", "kontrolluntersuchung"
    ],
    
    "restorative": [
        "füllung", "inlay", "onlay", "krone", "brücke", 
        "teilprothese", "vollprothese", "implantat"
    ],
    
    "surgical": [
        "extraktion", "weisheitszahn-op", "implantat-setzung",
        "wurzelspitzenresektion", "parodontalchirurgie"
    ],
    
    "cosmetic": [
        "bleaching", "veneers", "zahnschmuck", 
        "ästhetische zahnheilkunde"
    ]
}

# Deutsche Schmerzskala
GERMAN_PAIN_SCALE = {
    "levels": [
        "keine schmerzen", "leichte schmerzen", "mäßige schmerzen",
        "starke schmerzen", "sehr starke schmerzen", "unerträgliche schmerzen"
    ],
    
    "descriptions": [
        "pulsierend", "stechend", "ziehend", "pochend", "brennend",
        "dumpf", "scharf", "anhaltend", "periodisch"
    ]
}
