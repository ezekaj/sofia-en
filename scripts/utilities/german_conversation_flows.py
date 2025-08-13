# Deutsche Konversationsflüsse für Zahnarztpraxis-Rezeption

GREETING_RESPONSES = [
    "Guten Tag, ich bin Sofia, die virtuelle Assistentin der Zahnarztpraxis von Dr. Emanuela. Wie kann ich Ihnen heute helfen?",
    "Hallo, Zahnarztpraxis Dr. Emanuela, hier ist Sofia. Womit kann ich Ihnen behilflich sein?",
    "Guten Tag, hier Sofia von der Zahnarztpraxis Emanuela. Wie kann ich Sie unterstützen?"
]

APPOINTMENT_BOOKING_FLOWS = {
    "initial_request": [
        "Gerne! Ich helfe Ihnen dabei, einen Termin zu vereinbaren. Welche Art von Behandlung benötigen Sie?",
        "Perfekt! Ich prüfe sofort die Verfügbarkeit. Können Sie mir sagen, welche Behandlung Sie brauchen?",
        "Sehr gerne! Für welche Art von Behandlung möchten Sie einen Termin buchen?"
    ],
    
    "collecting_info": [
        "Perfekt. Jetzt benötige ich einige Daten. Können Sie mir Ihren vollständigen Namen nennen?",
        "Gut. Können Sie mir Ihre Telefonnummer für die Terminbuchung geben?",
        "Ausgezeichnet. Welches Datum würden Sie für den Termin bevorzugen?"
    ],
    
    "confirming_appointment": [
        "Perfekt! Ich habe Ihren Termin bestätigt. Ich sende Ihnen alle Details zu.",
        "Ausgezeichnet! Der Termin wurde erfolgreich gebucht.",
        "Alles bestätigt! Sie erhalten eine Bestätigung mit allen Details."
    ],
    
    "no_availability": [
        "Es tut mir leid, aber für dieses Datum haben wir keine Verfügbarkeit. Kann ich Ihnen Alternativen vorschlagen?",
        "Leider ist dieser Zeitslot bereits belegt. Passt es Ihnen, wenn ich andere Zeiten vorschlage?",
        "Wir haben zu diesem Zeitpunkt keine Verfügbarkeit. Soll ich andere Termine für Sie prüfen?"
    ]
}

EMERGENCY_RESPONSES = [
    "Ich verstehe, dass es sich um einen Notfall handelt. Beschreiben Sie kurz das Problem, damit ich Ihnen Priorität geben kann.",
    "Bei zahnärztlichen Notfällen versuchen wir immer, schnell eine Lösung zu finden. Sagen Sie mir, was passiert ist.",
    "Ich verstehe die Dringlichkeit. Können Sie mir kurz die Art der Schmerzen oder das Problem erklären?"
]

SERVICE_INQUIRY_RESPONSES = {
    "general_services": [
        "Gerne erkläre ich Ihnen unsere Leistungen. Suchen Sie Informationen zu einer bestimmten Behandlung?",
        "Wir bieten ein komplettes Spektrum zahnärztlicher Leistungen. Interessiert Sie etwas Bestimmtes?",
        "Ich gebe Ihnen sofort Informationen zu unseren Leistungen. Haben Sie bereits eine bestimmte Behandlung im Kopf?"
    ],
    
    "pricing": [
        "Ich suche Ihnen sofort die Kosteninformationen heraus. Für welche Behandlung möchten Sie den Preis wissen?",
        "Ich prüfe unsere Preislisten. Können Sie mir sagen, welche Leistung Sie benötigen?",
        "Gerne gebe ich Ihnen Informationen zu den Kosten. Welche Behandlung interessiert Sie?"
    ],
    
    "insurance": [
        "Ich prüfe sofort, ob Ihre Versicherung mit uns zusammenarbeitet. Können Sie mir den Namen der Gesellschaft nennen?",
        "Wir prüfen die Versicherungsabdeckung. Bei welcher Versicherung sind Sie versichert?",
        "Ich prüfe Ihnen sofort die Zusammenarbeit. Welche ist Ihre Krankenversicherung?"
    ]
}

CANCELLATION_FLOWS = {
    "understanding_request": [
        "Ich verstehe, dass Sie einen Termin absagen müssen. Können Sie mir die Details der Buchung geben?",
        "Kein Problem mit der Absage. Können Sie mir Datum und Uhrzeit des Termins nennen?",
        "Gerne helfe ich bei der Absage. Wann war Ihr Termin geplant?"
    ],
    
    "confirming_cancellation": [
        "Perfekt, ich habe Ihren Termin abgesagt. Möchten Sie für ein anderes Datum neu buchen?",
        "Die Absage wurde registriert. Soll ich Ihnen einen neuen Termin vorschlagen?",
        "Erledigt! Der Termin wurde abgesagt. Kann ich Ihnen helfen, einen neuen zu vereinbaren?"
    ]
}

RESCHEDULING_FLOWS = {
    "initial_request": [
        "Gerne! Ich helfe Ihnen, den Termin zu verschieben. Wann war der aktuelle Termin geplant?",
        "Kein Problem mit der Verschiebung. Können Sie mir das aktuelle Datum des Termins nennen?",
        "Sehr gerne! Auf welches Datum möchten Sie Ihren Termin verschieben?"
    ],
    
    "new_date_selection": [
        "Perfekt. Für welches neue Datum möchten Sie umbuchen?",
        "Gut. Wann würde Ihnen der neue Termin besser passen?",
        "Ausgezeichnet. Was wäre Ihre Präferenz für das neue Datum?"
    ]
}

FIRST_VISIT_GUIDANCE = [
    "Für den ersten Besuch benötigen Sie: Personalausweis, Versichertenkarte und eventuelle frühere Röntgenbilder.",
    "Zum ersten Termin bringen Sie bitte einen Ausweis, die Versichertenkarte und eine Liste Ihrer Medikamente mit.",
    "Für den ersten Termin: Personalausweis, Versichertenkarte und jegliche frühere medizinische Unterlagen."
]

PAYMENT_INQUIRIES = [
    "Ich gebe Ihnen sofort Informationen zu den Zahlungsmethoden, die wir akzeptieren.",
    "Ich prüfe die verfügbaren Zahlungsoptionen für Sie.",
    "Gerne erkläre ich Ihnen, wie Sie unsere Leistungen bezahlen können."
]

CLOSING_RESPONSES = [
    "Es war mir eine Freude, Ihnen zu helfen! Falls Sie weitere Fragen haben, zögern Sie nicht, uns zu kontaktieren.",
    "Perfekt! Sollten Sie noch etwas brauchen, bin ich immer hier, um Ihnen zu helfen.",
    "Ausgezeichnet! Für weitere Informationen können Sie uns jederzeit wieder kontaktieren."
]

EMPATHY_RESPONSES = {
    "pain": [
        "Es tut mir leid, dass Sie Schmerzen haben. Wir versuchen, Ihnen so schnell wie möglich einen Termin zu geben.",
        "Ich verstehe, wie unangenehm das sein kann. Ich helfe Ihnen sofort, eine Lösung zu finden.",
        "Ich verstehe Ihr Unbehagen. Schauen wir, wie wir Ihnen schnell helfen können."
    ],
    
    "anxiety": [
        "Ich verstehe Ihre Sorge. Unser Team ist sehr darauf bedacht, dass sich die Patienten wohlfühlen.",
        "Es ist normal, etwas nervös zu sein. Dr. Emanuela ist sehr einfühlsam und verständnisvoll.",
        "Ich verstehe Ihre Besorgnis. Wir schaffen immer eine entspannte Atmosphäre für unsere Patienten."
    ],
    
    "cost_concerns": [
        "Ich verstehe, dass die Kosten eine Sorge sind. Wir können Ratenzahlungsoptionen besprechen.",
        "Ich verstehe Ihre finanziellen Sorgen. Wir bieten verschiedene Zahlungslösungen an.",
        "Es ist normal, sich wegen der Kosten Sorgen zu machen. Wir können gemeinsam die beste Lösung für Sie finden."
    ]
}

CLARIFICATION_REQUESTS = [
    "Entschuldigung, das habe ich nicht ganz verstanden. Können Sie das wiederholen oder spezifischer sein?",
    "Entschuldigung, können Sie mir das nochmal genauer erklären?",
    "Verzeihung, ich bin mir nicht sicher, ob ich das verstanden habe. Können Sie es mir nochmal erklären?"
]

HOLD_RESPONSES = [
    "Einen Moment bitte, ich prüfe das...",
    "Warten Sie kurz, während ich das überprüfe...",
    "Ich prüfe das sofort für Sie, einen Moment..."
]

COMMON_GERMAN_PHRASES = {
    "politeness": [
        "Bitte", "Danke", "Entschuldigung", "Es tut mir leid", 
        "Gerne", "Selbstverständlich", "Natürlich"
    ],
    
    "time_expressions": [
        "sofort", "unverzüglich", "so schnell wie möglich", "baldmöglichst",
        "heute noch", "bis morgen", "nächste Woche"
    ],
    
    "dental_context": [
        "Kontrolluntersuchung", "Zahnreinigung", "Zahnschmerzen",
        "zahnärztlicher Notfall", "erster Termin", "Routinekontrolle"
    ]
}

# Konversationsmuster für verschiedene Szenarien
CONVERSATION_PATTERNS = {
    "appointment_booking": [
        "greeting", "service_inquiry", "availability_check", 
        "info_collection", "confirmation", "closing"
    ],
    
    "emergency": [
        "greeting", "emergency_assessment", "urgent_scheduling", 
        "instructions", "confirmation"
    ],
    
    "information_request": [
        "greeting", "clarify_request", "provide_information", 
        "additional_help", "closing"
    ],
    
    "cancellation": [
        "greeting", "understand_request", "locate_appointment",
        "confirm_cancellation", "offer_rescheduling", "closing"
    ]
}
