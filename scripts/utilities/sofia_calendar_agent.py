#!/usr/bin/env python3
"""
Sofia Calendar Agent - Speziell für Kalender-Integration
"""
import asyncio
import logging
from livekit import agents, rtc
from livekit.agents import AgentSession, RoomInputOptions
from livekit.plugins import google, silero, noise_cancellation
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import existing Sofia components
from src.agent.prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from src.dental.dental_tools import (
    schedule_appointment,
    check_availability,
    get_clinic_info,
    gespraech_hoeflich_beenden,
    intelligente_antwort_mit_namen_erkennung
)

logger = logging.getLogger(__name__)

class CalendarSofiaAgent:
    def __init__(self):
        self.sessions = []
        self.vad = silero.VAD.load()
        self.stt = google.STT(
            language_code="de-DE",
            model="latest_long",
            single_utterance=False,
            interim_results=True
        )
        self.llm = google.LLM(model="gemini-2.0-flash-exp")
        self.tts = google.TTS(
            voice="de-DE-Wavenet-F",
            language_code="de-DE",
            speaking_rate=1.0
        )
        
    async def entrypoint(self, ctx: agents.JobContext):
        """Main entry point for the agent"""
        logger.info(f"Sofia Calendar Agent starting in room: {ctx.room.name}")
        print(f"🤖 Sofia verbindet sich mit Raum: {ctx.room.name}")
        
        # Initial greeting when connected
        initial_speech = agents.synthesis.SynthesisHandle(
            source=self.tts.synthesize(
                "Hallo! Ich bin Sofia, Ihre Zahnarzt-Assistentin. Wie kann ich Ihnen heute helfen?"
            )
        )
        
        # Create session with voice activity detection
        session = AgentSession(
            stt=self.stt,
            llm=self.llm,
            tts=self.tts,
            vad=self.vad,
            fnc_ctx=agents.FunctionContext(
                schedule_appointment=schedule_appointment,
                check_availability=check_availability,
                get_clinic_info=get_clinic_info,
                gespraech_hoeflich_beenden=gespraech_hoeflich_beenden,
                intelligente_antwort_mit_namen_erkennung=intelligente_antwort_mit_namen_erkennung,
            ),
            initial_context=AGENT_INSTRUCTION,
            before_llm_cb=lambda a: a.update_msg(
                instruction=SESSION_INSTRUCTION.format(
                    existing_context=AGENT_INSTRUCTION,
                    participant_name=ctx.room.local_participant.identity
                )
            )
        )
        
        # Track subscriptions for participants
        @ctx.room.on("track_subscribed")
        async def on_track_subscribed(
            track: rtc.Track,
            publication: rtc.TrackPublication,
            participant: rtc.RemoteParticipant,
        ):
            logger.info(f"Track subscribed from {participant.identity}: {track.kind}")
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                print(f"🎤 Höre {participant.identity} zu...")
                # Start the session with the audio track
                await session.start(track)
                # Play initial greeting
                await session.play(initial_speech)
        
        # Monitor participant connections
        @ctx.room.on("participant_connected")
        async def on_participant_connected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant connected: {participant.identity}")
            print(f"👋 {participant.identity} ist verbunden")
        
        @ctx.room.on("participant_disconnected")
        async def on_participant_disconnected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant disconnected: {participant.identity}")
            print(f"👋 {participant.identity} hat verlassen")
        
        # Keep the agent running
        self.sessions.append(session)

# Create the agent with specific room configuration
async def run_calendar_agent():
    """Run the agent with calendar-specific configuration"""
    
    # Configure for calendar integration
    worker_options = agents.WorkerOptions(
        entrypoint_fnc=CalendarSofiaAgent().entrypoint,
        ws_url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
        api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "secret"),
        # Force specific room name for calendar
        request_handler=lambda req: agents.JobRequest(
            job_id="calendar-sofia",
            room=rtc.Room(name="sofia-room"),
            token=""
        ) if req.room.name == "" else req
    )
    
    # Run the agent
    await agents.Worker(worker_options).run()

if __name__ == "__main__":
    print("🚀 Sofia Calendar Agent startet...")
    print("📅 Verbinde mit Kalender-Integration...")
    print("🎤 Warte auf Sprachverbindungen...")
    
    # Run the agent
    asyncio.run(run_calendar_agent())