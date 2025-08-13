# English conversation flows for dental practice reception

GREETING_RESPONSES = [
    "Good day, I'm Sofia, the virtual assistant at Dr. Smith's dental practice. How can I help you today?",
    "Hello, Dr. Smith's dental practice, this is Sofia. How may I assist you?",
    "Good day, this is Sofia from Dr. Smith's dental practice. How can I support you?"
]

APPOINTMENT_BOOKING_FLOWS = {
    "initial_request": [
        "Certainly! I'll help you schedule an appointment. What type of treatment do you need?",
        "Perfect! I'll check availability right away. Can you tell me what treatment you need?",
        "I'd be happy to help! What type of treatment would you like to book an appointment for?"
    ],
    
    "collecting_info": [
        "Perfect. Now I need some information. Can you give me your full name?",
        "Good. Can you provide your phone number for the appointment booking?",
        "Excellent. Which date would you prefer for the appointment?"
    ],
    
    "confirming_appointment": [
        "Perfect! I've confirmed your appointment. I'll send you all the details.",
        "Excellent! The appointment has been successfully booked.",
        "All confirmed! You'll receive a confirmation with all the details."
    ],
    
    "no_availability": [
        "I'm sorry, but we don't have availability for that date. May I suggest alternatives?",
        "Unfortunately, that time slot is already taken. Would you like me to suggest other times?",
        "We don't have availability at that time. Shall I check other appointments for you?"
    ]
}

EMERGENCY_RESPONSES = [
    "I understand this is an emergency. Please briefly describe the problem so I can prioritize your case.",
    "For dental emergencies, we always try to find a quick solution. Tell me what happened.",
    "I understand the urgency. Can you briefly explain the type of pain or problem?"
]

SERVICE_INQUIRY_RESPONSES = {
    "general_services": [
        "I'd be happy to explain our services. Are you looking for information about a specific treatment?",
        "We offer a complete range of dental services. Is there something specific you're interested in?",
        "I'll provide you with information about our services right away. Do you have a particular treatment in mind?"
    ],
    
    "pricing": [
        "I'll look up the cost information for you right away. Which treatment would you like pricing for?",
        "I'll check our price lists. Can you tell me which service you need?",
        "I'd be happy to provide cost information. Which treatment are you interested in?"
    ],
    
    "insurance": [
        "I'll check right away if your insurance works with us. Can you tell me the company name?",
        "We'll verify insurance coverage. Which insurance company are you with?",
        "I'll check the collaboration immediately. What's your health insurance?"
    ]
}

CANCELLATION_FLOWS = {
    "understanding_request": [
        "I understand you need to cancel an appointment. Can you give me the booking details?",
        "No problem with the cancellation. Can you tell me the date and time of the appointment?",
        "I'll gladly help with the cancellation. When was your appointment scheduled?"
    ],
    
    "confirming_cancellation": [
        "Perfect, I've cancelled your appointment. Would you like to rebook for another date?",
        "The cancellation has been registered. Shall I suggest a new appointment?",
        "Done! The appointment has been cancelled. Can I help you schedule a new one?"
    ]
}

RESCHEDULING_FLOWS = {
    "initial_request": [
        "Certainly! I'll help you reschedule the appointment. When was the current appointment scheduled?",
        "No problem with rescheduling. Can you tell me the current date of the appointment?",
        "I'd be happy to help! What date would you like to reschedule your appointment to?"
    ],
    
    "new_date_selection": [
        "Perfect. What new date would you like to reschedule to?",
        "Good. When would the new appointment suit you better?",
        "Excellent. What would be your preference for the new date?"
    ]
}

FIRST_VISIT_GUIDANCE = [
    "For your first visit, you'll need: ID, insurance card, and any previous X-rays.",
    "For your first appointment, please bring ID, insurance card, and a list of your medications.",
    "For the initial appointment: ID, insurance card, and any previous medical records."
]

PAYMENT_INQUIRIES = [
    "I'll provide you with information about the payment methods we accept right away.",
    "I'll check the available payment options for you.",
    "I'd be happy to explain how you can pay for our services."
]

CLOSING_RESPONSES = [
    "It was my pleasure to help you! If you have any other questions, don't hesitate to contact us.",
    "Perfect! If you need anything else, I'm always here to help.",
    "Excellent! For more information, you can contact us again anytime."
]

EMPATHY_RESPONSES = {
    "pain": [
        "I'm sorry you're in pain. We'll try to get you an appointment as soon as possible.",
        "I understand how uncomfortable that can be. I'll help you find a solution right away.",
        "I understand your discomfort. Let's see how we can help you quickly."
    ],
    
    "anxiety": [
        "I understand your concern. Our team is very focused on making patients feel comfortable.",
        "It's normal to feel a bit nervous. Dr. Smith is very gentle and understanding.",
        "I understand your worry. We always create a relaxed atmosphere for our patients."
    ],
    
    "cost_concerns": [
        "I understand that costs are a concern. We can discuss payment plan options.",
        "I understand your financial concerns. We offer various payment solutions.",
        "It's normal to worry about costs. We can work together to find the best solution for you."
    ]
}

CLARIFICATION_REQUESTS = [
    "I'm sorry, I didn't quite understand that. Could you repeat or be more specific?",
    "Sorry, could you explain that in more detail?",
    "Pardon me, I'm not sure I understood. Could you explain again?"
]

HOLD_RESPONSES = [
    "One moment please, I'm checking that...",
    "Hold on while I verify that...",
    "I'll check that for you right away, one moment..."
]

COMMON_ENGLISH_PHRASES = {
    "politeness": [
        "Please", "Thank you", "Excuse me", "I'm sorry", 
        "Certainly", "Of course", "Naturally"
    ],
    
    "time_expressions": [
        "immediately", "right away", "as soon as possible", "at your earliest convenience",
        "today", "by tomorrow", "next week"
    ],
    
    "dental_context": [
        "dental hygiene", "check-up", "cleaning", "filling", "extraction",
        "root canal", "crown", "bridge", "implant", "orthodontics"
    ]
}

# Function to get appropriate response based on context
def get_response(category, subcategory=None, index=0):
    """Get an appropriate response based on the category and subcategory"""
    if subcategory:
        if category in globals() and isinstance(globals()[category], dict):
            if subcategory in globals()[category]:
                responses = globals()[category][subcategory]
                return responses[index % len(responses)]
    else:
        if category in globals() and isinstance(globals()[category], list):
            responses = globals()[category]
            return responses[index % len(responses)]
    return "How can I help you?"

# Contextual response builder
def build_contextual_response(context_type, patient_info=None):
    """Build a contextual response based on the situation"""
    base_response = get_response(context_type)
    
    if patient_info and 'name' in patient_info:
        # Personalize with patient name
        base_response = base_response.replace("you", f"you, {patient_info['name']}")
    
    return base_response