from dotenv import load_dotenv
import logging
import asyncio

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from dental_tools import (
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
    termine_suchen,
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
                termine_suchen,
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
    
    # Generate initial greeting
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )
    
    # Überwachungsschleife für automatisches Gesprächsende
    async def monitor_conversation_end():
        """
        Überwacht den Gesprächsstatus und beendet die Verbindung SOFORT wenn nötig
        """
        while True:
            try:
                # Prüfe HÄUFIGER - alle 0.5 Sekunden für sofortiges Beenden
                await asyncio.sleep(0.5)
                
                # Prüfe ob das Gespräch beendet werden soll
                if agent.is_conversation_ended():
                    print("🔴 Gesprächsende erkannt - Beende Verbindung SOFORT!")
                    logger.info("Conversation end detected - Ending connection IMMEDIATELY")
                    
                    # SOFORT beenden - keine Wartezeit!
                    print("📞 Verbindung wird SOFORT beendet...")
                    logger.info("Ending connection immediately...")
                    
                    # Versuche die Verbindung ordnungsgemäß zu beenden
                    try:
                        await ctx.room.disconnect()
                        print("✅ Verbindung erfolgreich beendet")
                        logger.info("Connection ended successfully")
                    except Exception as disconnect_error:
                        print(f"⚠️ Fehler beim Beenden der Verbindung: {disconnect_error}")
                        logger.error(f"Error ending connection: {disconnect_error}")
                    
                    break
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Fehler in der Gesprächsüberwachung: {e}")
                await asyncio.sleep(5)  # Warte länger bei Fehlern
    
    # Starte die Überwachung als Background-Task
    monitor_task = asyncio.create_task(monitor_conversation_end())
    
    # Warte auf Shutdown oder Gesprächsende
    try:
        await ctx.wait_for_shutdown()
    except Exception as e:
        logger.info(f"Shutdown durch Gesprächsende: {e}")
    finally:
        # Cleanup
        monitor_task.cancel()
        print("🛑 Agent beendet")
        logger.info("Agent shutdown")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
