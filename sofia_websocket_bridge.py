#!/usr/bin/env python3
"""
Sofia WebSocket Bridge - Complete Browser Integration Solution
Provides real-time voice interaction between browser clients and Sofia agent
"""

import asyncio
import websockets
import json
import logging
import threading
import queue
import time
import io
import wave
import base64
from datetime import datetime
from typing import Dict, Set, Optional, Any
import concurrent.futures
import signal
import sys
import os
from pathlib import Path

# Audio processing imports
try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False
    print("Warning: speech_recognition not available")

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("Warning: OpenAI not available for transcription")

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("Warning: pygame not available for audio playback")

try:
    from google.cloud import texttospeech
    HAS_GOOGLE_TTS = True
except ImportError:
    HAS_GOOGLE_TTS = False
    print("Warning: Google TTS not available")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sofia_websocket_bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SofiaWebSocketBridge:
    """Main WebSocket bridge server for Sofia voice agent integration"""
    
    def __init__(self, host='localhost', port=8081):
        self.host = host
        self.port = port
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.sofia_sessions: Dict[str, Dict] = {}
        self.running = False
        
        # Audio processing setup
        self.audio_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.speech_recognizer = sr.Recognizer() if HAS_SPEECH_RECOGNITION else None
        
        # Sofia agent integration
        self.sofia_bridge_queue = queue.Queue()
        self.sofia_response_queue = queue.Queue()
        
        # Performance monitoring
        self.stats = {
            'connections': 0,
            'messages_processed': 0,
            'audio_chunks_processed': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        self.setup_audio_services()
        
    def setup_audio_services(self):
        """Initialize audio processing services"""
        logger.info("Setting up audio services...")
        
        # OpenAI setup for transcription
        if HAS_OPENAI and os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            logger.info("✅ OpenAI Whisper available for transcription")
        else:
            logger.info("⚠️ OpenAI Whisper not available, using Google Speech Recognition")
            
        # Google TTS setup
        if HAS_GOOGLE_TTS and os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            try:
                self.tts_client = texttospeech.TextToSpeechClient()
                self.tts_voice = texttospeech.VoiceSelectionParams(
                    language_code="de-DE",
                    name="de-DE-Wavenet-F",
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
                )
                self.tts_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,
                    pitch=0.0
                )
                logger.info("✅ Google TTS available")
            except Exception as e:
                logger.error(f"Google TTS setup failed: {e}")
                self.tts_client = None
        else:
            logger.info("⚠️ Google TTS not available")
            self.tts_client = None
            
        # Initialize pygame for audio playback
        if HAS_PYGAME:
            try:
                pygame.mixer.init(frequency=16000, size=-16, channels=1, buffer=1024)
                logger.info("✅ Pygame audio initialized")
            except Exception as e:
                logger.error(f"Pygame initialization failed: {e}")

    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"🚀 Starting Sofia WebSocket Bridge on {self.host}:{self.port}")
        
        # Start Sofia agent bridge in background
        self.sofia_thread = threading.Thread(target=self.sofia_agent_bridge, daemon=True)
        self.sofia_thread.start()
        
        self.running = True
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info("✅ Sofia WebSocket Bridge is running!")
            logger.info(f"🌐 Connect browsers to: ws://{self.host}:{self.port}")
            logger.info("📊 Health check: http://localhost:3005/sofia-websocket-test.html")
            
            # Keep server running
            try:
                await asyncio.Future()  # Run forever
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down Sofia WebSocket Bridge...")
                await self.shutdown()

    async def handle_client(self, websocket, path):
        """Handle individual client connections"""
        client_id = f"client_{int(time.time() * 1000)}_{id(websocket)}"
        self.clients[client_id] = websocket
        self.stats['connections'] += 1
        
        logger.info(f"👤 New client connected: {client_id}")
        
        # Initialize client session
        self.sofia_sessions[client_id] = {
            'conversation_history': [],
            'context': {'language': 'de', 'mode': 'dental_receptionist'},
            'last_activity': time.time(),
            'audio_buffer': b'',
            'transcription_queue': []
        }
        
        try:
            # Send welcome message
            await self.send_to_client(client_id, {
                'type': 'connected',
                'client_id': client_id,
                'message': 'Mit Sofia WebSocket Bridge verbunden!',
                'capabilities': {
                    'transcription': HAS_OPENAI or HAS_SPEECH_RECOGNITION,
                    'text_to_speech': HAS_GOOGLE_TTS,
                    'audio_playback': HAS_PYGAME
                }
            })
            
            # Handle messages
            async for message in websocket:
                await self.process_client_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"👋 Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"❌ Error handling client {client_id}: {e}")
            self.stats['errors'] += 1
        finally:
            # Cleanup
            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.sofia_sessions:
                del self.sofia_sessions[client_id]

    async def process_client_message(self, client_id: str, message: str):
        """Process messages from browser clients"""
        try:
            data = json.loads(message)
            message_type = data.get('type', 'unknown')
            
            self.stats['messages_processed'] += 1
            self.sofia_sessions[client_id]['last_activity'] = time.time()
            
            logger.debug(f"📨 Processing message type: {message_type} from {client_id}")
            
            if message_type == 'audio_chunk':
                await self.handle_audio_chunk(client_id, data)
            elif message_type == 'text_message':
                await self.handle_text_message(client_id, data)
            elif message_type == 'appointment_request':
                await self.handle_appointment_request(client_id, data)
            elif message_type == 'ping':
                await self.send_to_client(client_id, {'type': 'pong', 'timestamp': time.time()})
            elif message_type == 'get_stats':
                await self.send_to_client(client_id, {'type': 'stats', 'data': self.get_stats()})
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {client_id}: {e}")
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Invalid message format'
            })
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")
            self.stats['errors'] += 1

    async def handle_audio_chunk(self, client_id: str, data: Dict):
        """Handle audio chunks from browser"""
        try:
            audio_data = base64.b64decode(data['audio_data'])
            session = self.sofia_sessions[client_id]
            
            # Add to audio buffer
            session['audio_buffer'] += audio_data
            self.stats['audio_chunks_processed'] += 1
            
            # Process if we have enough audio (e.g., 1-2 seconds worth)
            if len(session['audio_buffer']) > 32000:  # ~2 seconds at 16kHz
                await self.process_audio_transcription(client_id)
                
        except Exception as e:
            logger.error(f"Error handling audio chunk from {client_id}: {e}")
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Audio processing error'
            })

    async def process_audio_transcription(self, client_id: str):
        """Transcribe audio and send to Sofia"""
        session = self.sofia_sessions[client_id]
        audio_buffer = session['audio_buffer']
        session['audio_buffer'] = b''  # Clear buffer
        
        try:
            # Send status update
            await self.send_to_client(client_id, {
                'type': 'status',
                'message': 'Verarbeite Sprache...'
            })
            
            # Transcribe audio in background thread
            loop = asyncio.get_event_loop()
            transcription = await loop.run_in_executor(
                self.audio_executor,
                self.transcribe_audio,
                audio_buffer
            )
            
            if transcription:
                logger.info(f"🎤 Transcribed from {client_id}: {transcription}")
                
                # Send transcription to client
                await self.send_to_client(client_id, {
                    'type': 'transcription',
                    'text': transcription
                })
                
                # Process with Sofia
                await self.send_to_sofia(client_id, transcription)
            else:
                await self.send_to_client(client_id, {
                    'type': 'error',
                    'message': 'Sprache konnte nicht erkannt werden'
                })
                
        except Exception as e:
            logger.error(f"Transcription error for {client_id}: {e}")
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Fehler bei der Spracherkennung'
            })

    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using available services"""
        try:
            # Method 1: OpenAI Whisper (preferred)
            if HAS_OPENAI and os.getenv('OPENAI_API_KEY'):
                return self.transcribe_with_whisper(audio_data)
            
            # Method 2: Google Speech Recognition (fallback)
            elif HAS_SPEECH_RECOGNITION:
                return self.transcribe_with_google(audio_data)
            
            else:
                logger.warning("No transcription service available")
                return None
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

    def transcribe_with_whisper(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using OpenAI Whisper"""
        try:
            # Create temporary audio file
            audio_file = io.BytesIO()
            with wave.open(audio_file, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_data)
            
            audio_file.seek(0)
            audio_file.name = "audio.wav"  # Required by OpenAI API
            
            # Transcribe
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language="de"
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return None

    def transcribe_with_google(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using Google Speech Recognition"""
        try:
            # Convert audio data to AudioData object
            audio_file = io.BytesIO()
            with wave.open(audio_file, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_data)
            
            audio_file.seek(0)
            
            with sr.AudioFile(audio_file) as source:
                audio = self.speech_recognizer.record(source)
            
            # Recognize speech
            text = self.speech_recognizer.recognize_google(
                audio, 
                language='de-DE'
            )
            
            return text.strip()
            
        except sr.UnknownValueError:
            logger.debug("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Google Speech Recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            return None

    async def handle_text_message(self, client_id: str, data: Dict):
        """Handle text messages from browser"""
        try:
            text = data.get('text', '').strip()
            if not text:
                return
                
            logger.info(f"💬 Text message from {client_id}: {text}")
            
            # Send to Sofia
            await self.send_to_sofia(client_id, text)
            
        except Exception as e:
            logger.error(f"Error handling text message from {client_id}: {e}")

    async def send_to_sofia(self, client_id: str, user_input: str):
        """Send user input to Sofia agent and handle response"""
        try:
            session = self.sofia_sessions[client_id]
            
            # Add to conversation history
            session['conversation_history'].append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Send thinking status
            await self.send_to_client(client_id, {
                'type': 'status',
                'message': 'Sofia denkt nach...'
            })
            
            # Process with Sofia (simplified simulation for now)
            sofia_response = await self.process_with_sofia(client_id, user_input)
            
            if sofia_response:
                # Add to conversation history
                session['conversation_history'].append({
                    'role': 'assistant',
                    'content': sofia_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Send text response
                await self.send_to_client(client_id, {
                    'type': 'sofia_response',
                    'text': sofia_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Generate and send audio if TTS is available
                if self.tts_client:
                    audio_data = await self.generate_speech(sofia_response)
                    if audio_data:
                        await self.send_to_client(client_id, {
                            'type': 'sofia_audio',
                            'audio_data': base64.b64encode(audio_data).decode('utf-8'),
                            'format': 'mp3'
                        })
                        
        except Exception as e:
            logger.error(f"Error sending to Sofia for {client_id}: {e}")
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Fehler bei der Kommunikation mit Sofia'
            })

    async def process_with_sofia(self, client_id: str, user_input: str) -> Optional[str]:
        """Process user input with Sofia agent logic"""
        try:
            session = self.sofia_sessions[client_id]
            
            # Simple Sofia-like responses for demonstration
            # In production, this would interface with the actual Sofia agent
            
            user_input_lower = user_input.lower()
            
            if any(word in user_input_lower for word in ['termin', 'appointment', 'buchen', 'vereinbaren']):
                return "Gerne helfe ich Ihnen bei der Terminvereinbarung! Für welchen Tag hätten Sie gerne einen Termin?"
            
            elif any(word in user_input_lower for word in ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']):
                return "Ich schaue nach verfügbaren Terminen. Wie wäre es mit 10:00 Uhr oder 14:30 Uhr?"
            
            elif any(word in user_input_lower for word in ['10', '14', 'uhr', 'zeit']):
                return "Perfekt! Ich trage den Termin für Sie ein. Kann ich noch Ihren Namen und Ihre Telefonnummer haben?"
            
            elif any(word in user_input_lower for word in ['name', 'heiße', 'bin']):
                return "Vielen Dank! Ihr Termin ist eingetragen. Sie erhalten eine Bestätigung per E-Mail. Gibt es sonst noch etwas, womit ich Ihnen helfen kann?"
            
            elif any(word in user_input_lower for word in ['hallo', 'hi', 'guten tag']):
                return "Hallo! Ich bin Sofia, Ihre digitale Zahnarzthelferin. Wie kann ich Ihnen heute helfen?"
            
            elif any(word in user_input_lower for word in ['danke', 'vielen dank']):
                return "Gerne! Ich freue mich, dass ich Ihnen helfen konnte. Haben Sie noch weitere Fragen?"
            
            else:
                return "Das ist eine interessante Frage. Als Zahnarzthelferin kann ich Ihnen besonders gut bei Terminen, Behandlungsfragen oder allgemeinen Informationen helfen. Was genau möchten Sie wissen?"
                
        except Exception as e:
            logger.error(f"Error processing with Sofia: {e}")
            return "Entschuldigung, ich hatte ein kleines technisches Problem. Können Sie das bitte wiederholen?"

    async def generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech from text using Google TTS"""
        try:
            if not self.tts_client:
                return None
                
            # Create synthesis input
            input_text = texttospeech.SynthesisInput(text=text)
            
            # Generate speech
            response = self.tts_client.synthesize_speech(
                input=input_text,
                voice=self.tts_voice,
                audio_config=self.tts_config
            )
            
            return response.audio_content
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None

    async def handle_appointment_request(self, client_id: str, data: Dict):
        """Handle appointment booking requests"""
        try:
            appointment_data = data.get('appointment', {})
            
            # Send to calendar system (simplified)
            response = await self.book_appointment(appointment_data)
            
            await self.send_to_client(client_id, {
                'type': 'appointment_response',
                'success': response.get('success', False),
                'message': response.get('message', 'Terminbuchung verarbeitet'),
                'appointment_id': response.get('appointment_id')
            })
            
        except Exception as e:
            logger.error(f"Error handling appointment request: {e}")
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': 'Fehler bei der Terminbuchung'
            })

    async def book_appointment(self, appointment_data: Dict) -> Dict:
        """Book appointment with calendar system"""
        try:
            # In production, this would integrate with the actual calendar system
            # For now, simulate successful booking
            
            return {
                'success': True,
                'message': 'Termin erfolgreich gebucht!',
                'appointment_id': f"APPT_{int(time.time())}"
            }
            
        except Exception as e:
            logger.error(f"Appointment booking failed: {e}")
            return {
                'success': False,
                'message': 'Terminbuchung fehlgeschlagen'
            }

    async def send_to_client(self, client_id: str, message: Dict):
        """Send message to specific client"""
        try:
            if client_id in self.clients:
                websocket = self.clients[client_id]
                await websocket.send(json.dumps(message))
            else:
                logger.warning(f"Client {client_id} not found")
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for {client_id}")
            if client_id in self.clients:
                del self.clients[client_id]
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")

    def sofia_agent_bridge(self):
        """Background thread for Sofia agent integration"""
        logger.info("🤖 Sofia agent bridge started")
        
        # This would integrate with the actual Sofia agent
        # For now, it's a placeholder for the integration
        
        while self.running:
            try:
                time.sleep(1)
                # Process any background tasks
                
            except Exception as e:
                logger.error(f"Sofia bridge error: {e}")
                time.sleep(5)

    def get_stats(self) -> Dict:
        """Get server statistics"""
        return {
            **self.stats,
            'active_clients': len(self.clients),
            'active_sessions': len(self.sofia_sessions),
            'uptime': time.time() - self.stats['start_time']
        }

    async def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Close all client connections
        for client_id, websocket in list(self.clients.items()):
            try:
                await websocket.close()
            except:
                pass
                
        logger.info("✅ Sofia WebSocket Bridge shutdown complete")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sofia WebSocket Bridge')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8081, help='Port to bind to')
    parser.add_argument('--dev', action='store_true', help='Development mode')
    
    args = parser.parse_args()
    
    if args.dev:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🔧 Development mode enabled")
    
    # Create and start bridge
    bridge = SofiaWebSocketBridge(host=args.host, port=args.port)
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("📡 Received shutdown signal")
        asyncio.create_task(bridge.shutdown())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server
    try:
        asyncio.run(bridge.start_server())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()