#!/usr/bin/env python3
"""
Sofia Agent Adapter
===================

This adapter allows the Sofia WebSocket Bridge to interface with the existing
Sofia agent without requiring any modifications to the agent itself. It acts
as a translation layer between the WebSocket bridge and Sofia's tool ecosystem.

Key Features:
- Direct integration with Sofia's dental_tools
- Context management for conversation state
- German language processing and responses
- Appointment booking integration
- Session persistence and history
- Error handling and fallback responses
- Performance monitoring and caching

Author: Sofia Agent Adapter System
Version: 1.0.0
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import re
import uuid
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor

# Sofia agent imports
from src.dental.dental_tools import (
    schedule_appointment,
    check_availability,
    get_clinic_info,
    get_services_info,
    collect_patient_info,
    cancel_appointment,
    reschedule_appointment,
    answer_faq,
    get_insurance_info,
    get_payment_info,
    get_naechste_freie_termine,
    get_tagesplan_arzt,
    get_wochenuebersicht_arzt,
    termin_buchen_erweitert,
    get_patientenhistorie,
    termine_suchen_praxis,
    meine_termine_finden,
    medizinische_nachfragen_stellen,
    intelligente_terminbuchung_mit_nachfragen,
    namen_erkennen_und_speichern,
    intelligente_antwort_mit_namen_erkennung,
    gespraech_hoeflich_beenden,
    erkennung_gespraechsende_wunsch,
    intelligente_grund_nachfragen,
    conversational_repair,
    get_praxis_statistiken,
    termin_absagen,
    check_verfuegbarkeit_erweitert,
    parse_terminwunsch,
    get_aktuelle_datetime_info,
    get_intelligente_terminvorschlaege,
    termin_buchen_mit_details,
    termin_direkt_buchen,
    check_verfuegbarkeit_spezifisch,
    gespraech_beenden,
    notiz_hinzufuegen,
    gespraech_status,
    get_zeitabhaengige_begruessung,
    sofia_naechster_freier_termin,
    sofia_termin_an_bestimmtem_tag,
    sofia_terminvorschlaege_intelligent,
    sofia_heutige_termine_abrufen,
    sofia_meine_termine_finden_erweitert,
    termin_buchen_calendar_system,
    call_manager
)

from src.agent.prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Manages conversation context and state"""
    session_id: str
    user_name: str = ""
    phone_number: str = ""
    current_intent: str = ""
    conversation_history: List[Dict] = None
    appointment_context: Dict = None
    last_interaction: datetime = None
    language: str = "de-DE"
    conversation_state: str = "active"  # active, booking, confirming, ending
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.appointment_context is None:
            self.appointment_context = {}
        if self.last_interaction is None:
            self.last_interaction = datetime.now()

class IntentClassifier:
    """Classifies user intents from German text"""
    
    def __init__(self):
        # Intent patterns for German language
        self.intent_patterns = {
            'greeting': [
                r'\b(hallo|guten\s+tag|guten\s+morgen|guten\s+abend|hi|hey)\b',
                r'\b(servus|grüß\s+gott|moin)\b'
            ],
            'appointment_booking': [
                r'\b(termin|appointment|buchen|vereinbaren|reservieren)\b',
                r'\b(zahnarzt|behandlung|untersuchung|kontrolle)\b',
                r'\b(brauche\s+einen?\s+termin|möchte\s+einen?\s+termin)\b'
            ],
            'appointment_inquiry': [
                r'\b(wann|welche\s+termine|freie?\s+termine?)\b',
                r'\b(verfügbar|frei|möglich)\b',
                r'\b(nächste?\s+freie?\s+termin)\b'
            ],
            'appointment_cancellation': [
                r'\b(absagen|stornieren|cancel|löschen)\b',
                r'\b(kann\s+nicht|schaffe\s+nicht)\b'
            ],
            'clinic_info': [
                r'\b(öffnungszeiten|adresse|telefon|kontakt)\b',
                r'\b(wo\s+sind\s+sie|wie\s+erreiche)\b',
                r'\b(information|info|details)\b'
            ],
            'services_info': [
                r'\b(behandlung|service|leistung|angebot)\b',
                r'\b(was\s+bieten|welche\s+behandlung)\b'
            ],
            'goodbye': [
                r'\b(auf\s+wiedersehen|tschüss|bis\s+dann|ciao)\b',
                r'\b(danke|vielen\s+dank|bedanke)\b.*\b(ende|schluss|fertig)\b'
            ],
            'help': [
                r'\b(hilfe|help|was\s+kann|funktionen)\b',
                r'\b(wie\s+funktioniert|erklären)\b'
            ]
        }
        
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """Classify intent from user text"""
        text_lower = text.lower()
        best_intent = 'general_question'
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                if matches > 0:
                    score += matches * 0.3
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent, best_score

class ResponseGenerator:
    """Generates appropriate responses based on context and intent"""
    
    def __init__(self):
        self.fallback_responses = {
            'general_question': [
                "Gerne helfe ich Ihnen weiter. Wie kann ich Ihnen behilflich sein?",
                "Was kann ich für Sie tun?",
                "Ich bin hier, um Ihnen zu helfen. Was möchten Sie wissen?"
            ],
            'greeting': [
                "Hallo! Schön, dass Sie da sind. Wie kann ich Ihnen heute helfen?",
                "Guten Tag! Womit kann ich Ihnen behilflich sein?",
                "Herzlich willkommen! Was kann ich für Sie tun?"
            ],
            'error': [
                "Entschuldigung, das habe ich nicht verstanden. Können Sie das bitte wiederholen?",
                "Es tut mir leid, ich konnte Ihre Anfrage nicht verarbeiten. Versuchen Sie es bitte erneut.",
                "Leider gab es ein Problem. Bitte formulieren Sie Ihre Anfrage noch einmal."
            ]
        }
    
    def get_fallback_response(self, intent: str = 'general_question') -> str:
        """Get a fallback response for the given intent"""
        responses = self.fallback_responses.get(intent, self.fallback_responses['general_question'])
        import random
        return random.choice(responses)

class SofiaAgentAdapter:
    """
    Main adapter class that bridges WebSocket clients with Sofia agent tools
    """
    
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}
        self.intent_classifier = IntentClassifier()
        self.response_generator = ResponseGenerator()
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Sofia tools registry with metadata
        self.sofia_tools = {
            'greeting': {
                'function': get_zeitabhaengige_begruessung,
                'description': 'Time-based greeting',
                'params': []
            },
            'appointment_booking': {
                'function': intelligente_terminbuchung_mit_nachfragen,
                'description': 'Intelligent appointment booking with follow-up questions',
                'params': ['user_message', 'patient_name']
            },
            'appointment_inquiry': {
                'function': get_intelligente_terminvorschlaege,
                'description': 'Get intelligent appointment suggestions',
                'params': ['days_ahead', 'preferred_time']
            },
            'next_free_appointment': {
                'function': sofia_naechster_freier_termin,
                'description': 'Find next available appointment',
                'params': []
            },
            'specific_date_check': {
                'function': sofia_termin_an_bestimmtem_tag,
                'description': 'Check availability for specific date',
                'params': ['date']
            },
            'clinic_info': {
                'function': get_clinic_info,
                'description': 'Get clinic information',
                'params': []
            },
            'services_info': {
                'function': get_services_info,
                'description': 'Get services information',
                'params': []
            },
            'today_appointments': {
                'function': sofia_heutige_termine_abrufen,
                'description': 'Get today\'s appointments',
                'params': []
            },
            'patient_appointments': {
                'function': sofia_meine_termine_finden_erweitert,
                'description': 'Find patient appointments',
                'params': ['phone_number']
            },
            'conversation_end': {
                'function': gespraech_hoeflich_beenden,
                'description': 'End conversation politely',
                'params': ['user_message']
            },
            'general_response': {
                'function': intelligente_antwort_mit_namen_erkennung,
                'description': 'Generate intelligent response with name recognition',
                'params': ['user_message', 'patient_name', 'conversation_context']
            },
            'calendar_booking': {
                'function': termin_buchen_calendar_system,
                'description': 'Book appointment through calendar system',
                'params': ['patient_name', 'phone_number', 'date', 'time', 'treatment_type']
            }
        }
        
        # Performance statistics
        self.stats = {
            'total_requests': 0,
            'successful_responses': 0,
            'errors': 0,
            'tool_usage': {},
            'average_response_time': 0.0,
            'active_sessions': 0
        }
        
        logger.info(f"Sofia Agent Adapter initialized with {len(self.sofia_tools)} tools")
    
    def create_session(self, session_id: str, user_name: str = "", phone_number: str = "") -> ConversationContext:
        """Create a new conversation session"""
        context = ConversationContext(
            session_id=session_id,
            user_name=user_name,
            phone_number=phone_number
        )
        
        self.sessions[session_id] = context
        self.stats['active_sessions'] = len(self.sessions)
        
        logger.info(f"Created new session: {session_id}")
        return context
    
    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            return self.create_session(session_id)
        
        session = self.sessions[session_id]
        session.last_interaction = datetime.now()
        return session
    
    def update_session_info(self, session_id: str, user_name: str = None, phone_number: str = None):
        """Update session information"""
        session = self.get_session(session_id)
        
        if user_name:
            session.user_name = user_name
        if phone_number:
            session.phone_number = phone_number
        
        logger.info(f"Updated session {session_id}: {session.user_name}, {session.phone_number}")
    
    async def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process user message and generate appropriate response
        """
        start_time = datetime.now()
        self.stats['total_requests'] += 1
        
        try:
            # Get or create session
            session = self.get_session(session_id)
            
            # Add message to conversation history
            session.conversation_history.append({
                'type': 'user',
                'message': user_message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Classify intent
            intent, confidence = self.intent_classifier.classify_intent(user_message)
            session.current_intent = intent
            
            logger.info(f"Session {session_id}: Intent '{intent}' (confidence: {confidence:.2f})")
            
            # Process based on intent
            response = await self._process_intent(session, user_message, intent, confidence)
            
            # Add response to conversation history
            session.conversation_history.append({
                'type': 'sofia',
                'message': response.get('message', ''),
                'timestamp': datetime.now().isoformat()
            })
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(intent, processing_time, success=True)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {e}")
            self._update_stats('error', 0, success=False)
            
            return {
                'success': False,
                'message': self.response_generator.get_fallback_response('error'),
                'intent': 'error',
                'session_id': session_id
            }
    
    async def _process_intent(self, session: ConversationContext, user_message: str, intent: str, confidence: float) -> Dict[str, Any]:
        """Process user message based on classified intent"""
        
        # Handle greeting
        if intent == 'greeting':
            return await self._handle_greeting(session, user_message)
        
        # Handle appointment booking
        elif intent == 'appointment_booking':
            return await self._handle_appointment_booking(session, user_message)
        
        # Handle appointment inquiry
        elif intent == 'appointment_inquiry':
            return await self._handle_appointment_inquiry(session, user_message)
        
        # Handle appointment cancellation
        elif intent == 'appointment_cancellation':
            return await self._handle_appointment_cancellation(session, user_message)
        
        # Handle clinic information requests
        elif intent == 'clinic_info':
            return await self._handle_clinic_info(session, user_message)
        
        # Handle services information
        elif intent == 'services_info':
            return await self._handle_services_info(session, user_message)
        
        # Handle goodbye
        elif intent == 'goodbye':
            return await self._handle_goodbye(session, user_message)
        
        # Handle help requests
        elif intent == 'help':
            return await self._handle_help(session, user_message)
        
        # Default to general intelligent response
        else:
            return await self._handle_general_response(session, user_message)
    
    async def _handle_greeting(self, session: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Handle greeting messages"""
        try:
            result = await self._execute_sofia_tool(
                'greeting',
                session,
                {}
            )
            
            greeting_message = result.get('message', 'Hallo! Wie kann ich Ihnen helfen?')
            
            # Personalize if name is known
            if session.user_name:
                greeting_message = f"Hallo {session.user_name}! " + greeting_message
            
            return {
                'success': True,
                'message': greeting_message,
                'intent': 'greeting',
                'session_id': session.session_id,
                'next_suggestions': [
                    'Ich möchte einen Termin buchen',
                    'Wann haben Sie freie Termine?',
                    'Welche Behandlungen bieten Sie an?'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error handling greeting: {e}")
            return {
                'success': False,
                'message': self.response_generator.get_fallback_response('greeting'),
                'intent': 'greeting',
                'session_id': session.session_id
            }
    
    async def _handle_appointment_booking(self, session: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Handle appointment booking requests"""
        try:
            session.conversation_state = 'booking'
            
            result = await self._execute_sofia_tool(
                'appointment_booking',
                session,
                {
                    'user_message': user_message,
                    'patient_name': session.user_name or 'Patient'
                }
            )
            
            response_message = result.get('message', 'Gerne helfe ich Ihnen bei der Terminbuchung.')
            
            # Check if we need more information
            needs_info = []
            if not session.user_name:
                needs_info.append('name')
            if not session.phone_number:
                needs_info.append('phone')
            
            return {
                'success': True,
                'message': response_message,
                'intent': 'appointment_booking',
                'session_id': session.session_id,
                'conversation_state': 'booking',
                'needs_info': needs_info,
                'next_steps': [
                    'Wann hätten Sie gerne einen Termin?',
                    'Welche Behandlung benötigen Sie?'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error handling appointment booking: {e}")
            return {
                'success': False,
                'message': 'Entschuldigung, bei der Terminbuchung ist ein Fehler aufgetreten.',
                'intent': 'appointment_booking',
                'session_id': session.session_id
            }
    
    async def _handle_appointment_inquiry(self, session: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Handle appointment availability inquiries"""
        try:
            # Check if asking for next free appointment
            if any(phrase in user_message.lower() for phrase in ['nächste', 'nächster', 'next', 'freie']):
                result = await self._execute_sofia_tool(
                    'next_free_appointment',
                    session,
                    {}
                )
            else:
                # General appointment suggestions
                result = await self._execute_sofia_tool(
                    'appointment_inquiry',
                    session,
                    {
                        'days_ahead': 14,
                        'preferred_time': 'morning'
                    }
                )
            
            return {
                'success': True,
                'message': result.get('message', 'Hier sind unsere verfügbaren Termine...'),
                'intent': 'appointment_inquiry',
                'session_id': session.session_id,
                'available_times': result.get('suggestions', []),
                'next_suggestions': [
                    'Ich möchte einen dieser Termine buchen',
                    'Haben Sie auch Termine am Nachmittag?'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error handling appointment inquiry: {e}")
            return {
                'success': False,
                'message': 'Entschuldigung, ich konnte keine verfügbaren Termine abrufen.',
                'intent': 'appointment_inquiry',
                'session_id': session.session_id
            }
    
    async def _handle_appointment_cancellation(self, session: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Handle appointment cancellation requests"""
        try:
            # First, try to find patient's appointments
            if session.phone_number:
                appointments_result = await self._execute_sofia_tool(
                    'patient_appointments',
                    session,
                    {'phone_number': session.phone_number}
                )
                
                if appointments_result.get('appointments'):
                    return {
                        'success': True,
                        'message': 'Welchen Termin möchten Sie absagen? ' + appointments_result.get('message', ''),
                        'intent': 'appointment_cancellation',
                        'session_id': session.session_id,
                        'appointments': appointments_result.get('appointments', []),
                        'conversation_state': 'cancelling'
                    }
            
            return {
                'success': True,
                'message': 'Um Ihren Termin abzusagen, benötige ich Ihre Telefonnummer oder Ihren Namen.',
                'intent': 'appointment_cancellation',
                'session_id': session.session_id,
                'needs_info': ['phone', 'name']
            }
            
        except Exception as e:
            logger.error(f"Error handling appointment cancellation: {e}")
            return {
                'success': False,
                'message': 'Bei der Terminabsage ist ein Fehler aufgetreten.',
                'intent': 'appointment_cancellation',
                'session_id': session.session_id
            }
    
    async def _handle_clinic_info(self, session: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Handle clinic information requests"""
        try:
            result = await self._execute_sofia_tool(
                'clinic_info',
                session,
                {}
            )
            
            return {
                'success': True,
                'message': result.get('message', 'Hier sind unsere Praxisinformationen...'),
                'intent': 'clinic_info',
                'session_id': session.session_id,
                'clinic_info': result.get('info', {}),
                'next_suggestions': [
                    'Ich möchte einen Termin buchen',
                    'Welche Behandlungen bieten Sie an?'
                ]
            }
            
        } except Exception as e:
            logger.error(f"Error handling clinic info: {e}")
            return {
                'success': False,
                'message': 'Entschuldigung, ich konnte die Praxisinformationen nicht abrufen.',
                'intent': 'clinic_info',
                'session_id': session.session_id
            }
    
    async def _handle_services_info(self, session: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Handle services information requests"""
        try:
            result = await self._execute_sofia_tool(
                'services_info',
                session,
                {}
            )
            
            return {
                'success': True,
                'message': result.get('message', 'Hier sind unsere Behandlungsangebote...'),
                'intent': 'services_info',
                'session_id': session.session_id,
                'services': result.get('services', []),
                'next_suggestions': [
                    'Ich möchte einen Termin für eine Kontrolle',
                    'Was kostet eine Behandlung?'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error handling services info: {e}")
            return {
                'success': False,
                'message': 'Entschuldigung, ich konnte die Behandlungsinformationen nicht abrufen.',
                'intent': 'services_info',
                'session_id': session.session_id
            }
    
    async def _handle_goodbye(self, session: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Handle goodbye messages"""
        try:
            session.conversation_state = 'ending'
            
            result = await self._execute_sofia_tool(
                'conversation_end',
                session,
                {'user_message': user_message}
            )
            
            return {
                'success': True,
                'message': result.get('message', 'Auf Wiedersehen und vielen Dank!'),
                'intent': 'goodbye',
                'session_id': session.session_id,
                'conversation_end': True
            }
            
        except Exception as e:
            logger.error(f"Error handling goodbye: {e}")
            return {
                'success': True,
                'message': 'Auf Wiedersehen und vielen Dank für Ihren Besuch!',
                'intent': 'goodbye',
                'session_id': session.session_id,
                'conversation_end': True
            }
    
    async def _handle_help(self, session: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Handle help requests"""
        help_message = """Ich kann Ihnen bei folgenden Aufgaben helfen:

🦷 Terminbuchung und -verwaltung
📅 Verfügbare Termine anzeigen
ℹ️ Praxisinformationen
🏥 Behandlungsangebote
📞 Kontaktdaten

Sagen Sie einfach, womit ich Ihnen helfen kann!"""
        
        return {
            'success': True,
            'message': help_message,
            'intent': 'help',
            'session_id': session.session_id,
            'capabilities': [
                'Terminbuchung',
                'Terminabfrage',
                'Praxisinformationen',
                'Behandlungsangebote',
                'Kontaktdaten'
            ]
        }
    
    async def _handle_general_response(self, session: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Handle general questions with intelligent responses"""
        try:
            result = await self._execute_sofia_tool(
                'general_response',
                session,
                {
                    'user_message': user_message,
                    'patient_name': session.user_name or 'Patient',
                    'conversation_context': session.conversation_history[-5:]  # Last 5 messages
                }
            )
            
            return {
                'success': True,
                'message': result.get('message', self.response_generator.get_fallback_response()),
                'intent': 'general_question',
                'session_id': session.session_id,
                'suggestions': [
                    'Ich möchte einen Termin buchen',
                    'Wann haben Sie geöffnet?',
                    'Welche Behandlungen bieten Sie an?'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error handling general response: {e}")
            return {
                'success': False,
                'message': self.response_generator.get_fallback_response('general_question'),
                'intent': 'general_question',
                'session_id': session.session_id
            }
    
    async def _execute_sofia_tool(self, tool_name: str, session: ConversationContext, params: Dict) -> Dict[str, Any]:
        """Execute a Sofia tool function"""
        if tool_name not in self.sofia_tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_info = self.sofia_tools[tool_name]
        tool_function = tool_info['function']
        
        try:
            # Execute in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._run_tool_function,
                tool_function,
                params
            )
            
            # Update statistics
            if tool_name not in self.stats['tool_usage']:
                self.stats['tool_usage'][tool_name] = 0
            self.stats['tool_usage'][tool_name] += 1
            
            logger.info(f"Executed Sofia tool '{tool_name}' for session {session.session_id}")
            
            return result if result else {'success': False, 'message': 'Tool returned no result'}
            
        except Exception as e:
            logger.error(f"Error executing Sofia tool '{tool_name}': {e}")
            raise
    
    def _run_tool_function(self, tool_function, params: Dict) -> Dict[str, Any]:
        """Run tool function synchronously"""
        try:
            if params:
                return tool_function(**params)
            else:
                return tool_function()
        except Exception as e:
            logger.error(f"Tool function error: {e}")
            return {'success': False, 'message': f'Tool execution error: {str(e)}'}
    
    async def book_appointment(self, session_id: str, patient_name: str, phone_number: str, 
                             date: str, time: str, treatment_type: str = 'Beratung') -> Dict[str, Any]:
        """Book an appointment through the calendar system"""
        try:
            session = self.get_session(session_id)
            session.user_name = patient_name
            session.phone_number = phone_number
            session.conversation_state = 'confirming'
            
            result = await self._execute_sofia_tool(
                'calendar_booking',
                session,
                {
                    'patient_name': patient_name,
                    'phone_number': phone_number,
                    'date': date,
                    'time': time,
                    'treatment_type': treatment_type
                }
            )
            
            if result.get('success', False):
                session.appointment_context = {
                    'patient_name': patient_name,
                    'phone_number': phone_number,
                    'date': date,
                    'time': time,
                    'treatment_type': treatment_type,
                    'appointment_id': result.get('appointment_id')
                }
                
                return {
                    'success': True,
                    'message': f"Ihr Termin wurde erfolgreich gebucht für {date} um {time} Uhr.",
                    'appointment': result.get('appointment'),
                    'session_id': session_id,
                    'confirmation_needed': False
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', 'Terminbuchung fehlgeschlagen.'),
                    'session_id': session_id,
                    'alternatives': result.get('alternatives', [])
                }
                
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {
                'success': False,
                'message': 'Bei der Terminbuchung ist ein Fehler aufgetreten.',
                'session_id': session_id
            }
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old inactive sessions"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session.last_interaction < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            logger.info(f"Cleaned up old session: {session_id}")
        
        self.stats['active_sessions'] = len(self.sessions)
    
    def _update_stats(self, intent: str, processing_time: float, success: bool):
        """Update performance statistics"""
        if success:
            self.stats['successful_responses'] += 1
        else:
            self.stats['errors'] += 1
        
        # Update average response time
        total_responses = self.stats['successful_responses'] + self.stats['errors']
        if total_responses > 0:
            current_avg = self.stats['average_response_time']
            self.stats['average_response_time'] = (
                (current_avg * (total_responses - 1) + processing_time) / total_responses
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            **self.stats,
            'total_tools': len(self.sofia_tools),
            'active_sessions': len(self.sessions)
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            'session_id': session.session_id,
            'user_name': session.user_name,
            'phone_number': session.phone_number,
            'current_intent': session.current_intent,
            'conversation_state': session.conversation_state,
            'last_interaction': session.last_interaction.isoformat(),
            'message_count': len(session.conversation_history),
            'language': session.language
        }

# Singleton instance for global access
sofia_adapter = SofiaAgentAdapter()

# Async wrapper functions for easy integration
async def process_user_message(session_id: str, message: str) -> Dict[str, Any]:
    """Process user message through Sofia adapter"""
    return await sofia_adapter.process_message(session_id, message)

async def book_user_appointment(session_id: str, patient_name: str, phone_number: str,
                              date: str, time: str, treatment_type: str = 'Beratung') -> Dict[str, Any]:
    """Book appointment through Sofia adapter"""
    return await sofia_adapter.book_appointment(session_id, patient_name, phone_number, 
                                               date, time, treatment_type)

def update_user_info(session_id: str, user_name: str = None, phone_number: str = None):
    """Update user information in session"""
    sofia_adapter.update_session_info(session_id, user_name, phone_number)

def get_adapter_stats() -> Dict[str, Any]:
    """Get adapter statistics"""
    return sofia_adapter.get_stats()

def cleanup_sessions():
    """Clean up old sessions"""
    sofia_adapter.cleanup_old_sessions()

if __name__ == "__main__":
    # Test the adapter
    import asyncio
    
    async def test_adapter():
        adapter = SofiaAgentAdapter()
        
        # Test greeting
        result = await adapter.process_message("test-session", "Hallo!")
        print("Greeting test:", result)
        
        # Test appointment booking
        result = await adapter.process_message("test-session", "Ich möchte einen Termin buchen")
        print("Appointment booking test:", result)
        
        # Test clinic info
        result = await adapter.process_message("test-session", "Wann haben Sie geöffnet?")
        print("Clinic info test:", result)
        
        print("Adapter stats:", adapter.get_stats())
    
    asyncio.run(test_adapter())