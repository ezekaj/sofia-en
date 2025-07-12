from dotenv import load_dotenv
import logging
import asyncio

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
from src.prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from src.dental_tools import (
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
    call_manager  # Import the call manager
)

load_dotenv()

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DentalReceptionist(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",  # Female voice for German
                language="de-DE",  # German language
                temperature=0.7,
            ),
            tools=[
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
                get_zeitabhaengige_begruessung
            ],
        )
        self.should_end_conversation = False
    
    async def handle_response(self, response: str) -> str:
        """
        Verarbeitet die Antwort und prüft auf Gesprächsende-Signal
        KRITISCH: Bei Ende-Signal SOFORT beenden!
        """
        # Prüfe auf Ende-Signal
        if "*[CALL_END_SIGNAL]*" in response:
            self.should_end_conversation = True
            logging.info("🔴 Gesprächsende-Signal erkannt - Gespräch wird SOFORT beendet")
            # Entferne das Signal aus der Antwort
            response = response.replace("*[CALL_END_SIGNAL]*", "")
            
            # SOFORT beenden - keine weiteren Nachrichten!
            logging.info("🚨 KRITISCH: Gespräch MUSS SOFORT beendet werden!")
            
        # Prüfe auch den CallManager-Status
        if call_manager.is_conversation_ended():
            self.should_end_conversation = True
            logging.info("🔴 CallManager signalisiert Gesprächsende - SOFORT beenden")
            
        return response
    
    def is_conversation_ended(self) -> bool:
        """
        Prüft, ob das Gespräch beendet werden soll
        """
        return self.should_end_conversation or call_manager.is_conversation_ended()


async def entrypoint(ctx: agents.JobContext):
    print("🎤 Starte deutsche Zahnarzt-Assistentin mit Audio-Input...")
    logger.info("Starting German dental assistant agent")
    
    # Create the agent
    agent = DentalReceptionist()
    
    # Enhanced room input options for better audio reception
    room_input_options = RoomInputOptions(
        audio_enabled=True,
        video_enabled=False,
        # Enhanced noise cancellation
        noise_cancellation=noise_cancellation.BVC(),
    )
    
    # Start session
    session = AgentSession()
    
    # Add event handlers before connecting
    @ctx.room.on("track_published")
    async def on_track_published(publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        print(f"🎵 Audio-Track erkannt: {publication.track_info.name}")
        logger.info(f"Audio track published: {publication.track_info.name}")
        
        if publication.track_info.kind == rtc.TrackKind.KIND_AUDIO:
            print("✅ Mikrofon-Input aktiv!")
            logger.info("Microphone input active")
            
            # Subscribe to the audio track
            track = await publication.track()
            if track:
                print("🎤 Höre zu...")
                logger.info("Listening to audio track")
                
                # Start processing audio
                await session.process_track(track)
    
    @ctx.room.on("participant_connected")
    async def on_participant_connected(participant: rtc.RemoteParticipant):
        print(f"👋 Teilnehmer verbunden: {participant.identity}")
        logger.info(f"Participant connected: {participant.identity}")
    
    @ctx.room.on("data_received")
    async def on_data_received(data: rtc.DataPacket):
        print(f"📨 Daten empfangen: {data.data}")
        logger.info(f"Data received: {data.data}")
    
    # Connect to the room
    await ctx.connect()
    print("🔗 Mit LiveKit-Raum verbunden")
    
    # Start the agent session
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=room_input_options,
    )
    
    print("🎯 Bereit zum Zuhören! Sprechen Sie jetzt...")
    logger.info("Agent ready to listen")
    
    # Generate initial greeting with AUTOMATIC date/time detection
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION + "\n\n**WICHTIG**: Rufen Sie SOFORT `get_zeitabhaengige_begruessung()` für die automatische Begrüßung auf!",
    )
    
    # KEIN automatisches Gesprächsende-Monitoring
    # Sofia läuft kontinuierlich ohne Unterbrechungen
    
    # KEIN automatisches Monitoring - Sofia läuft kontinuierlich
    
    # Warte auf Shutdown - OHNE automatisches Beenden
    try:
        # Endlos-Schleife - Agent läuft kontinuierlich
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Agent manuell beendet")
    except Exception as e:
        logger.info(f"Agent Fehler: {e}")
        # Bei Fehlern weiter laufen lassen
        await asyncio.sleep(5)
    finally:
        # Cleanup nur bei echtem Shutdown
        print("🛑 Agent beendet")
        logger.info("Agent shutdown")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
