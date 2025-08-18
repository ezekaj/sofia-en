from dotenv import load_dotenv
import logging
import asyncio

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
from src.agent.prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
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
    get_next_available_appointments,
    get_doctor_daily_schedule,
    get_doctor_weekly_overview,
    book_appointment_extended,
    get_patient_history,
    search_practice_appointments,
    find_my_appointments,
    ask_medical_followup_questions,
    smart_appointment_booking_with_followups,
    recognize_and_save_name,
    smart_response_with_name_recognition,
    end_conversation_politely,
    detect_conversation_end_wish,
    smart_reason_followup,
    conversational_repair,
    get_practice_statistics,
    cancel_appointment_by_id,
    check_availability_extended,
    parse_appointment_request,
    get_current_datetime_info,
    get_smart_appointment_suggestions,
    book_appointment_with_details,
    book_appointment_directly,
    check_specific_availability,
    end_conversation,
    add_note,
    conversation_status,
    get_time_based_greeting,
    sofia_next_available_appointment,
    sofia_appointment_on_specific_day,
    sofia_smart_appointment_suggestions,
    sofia_get_todays_appointments,
    sofia_find_my_appointments_extended,
    book_appointment_calendar_system,  # NEW: Calendar integration booking
    emergency_prioritization,  # Emergency handling
    phd_stomatology_first_aid_guidance,  # PhD first aid guidance
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
                voice="Aoede",  # Female voice
                language="en-US",  # English language
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
                get_next_available_appointments,
                get_doctor_daily_schedule,
                get_doctor_weekly_overview,
                book_appointment_extended,
                get_patient_history,
                search_practice_appointments,
                find_my_appointments,
                ask_medical_followup_questions,
                smart_appointment_booking_with_followups,
                recognize_and_save_name,
                smart_response_with_name_recognition,
                end_conversation_politely,
                detect_conversation_end_wish,
                smart_reason_followup,
                conversational_repair,
                get_practice_statistics,
                cancel_appointment_by_id,
                check_availability_extended,
                parse_appointment_request,
                get_current_datetime_info,
                get_smart_appointment_suggestions,
                book_appointment_with_details,
                book_appointment_directly,
                check_specific_availability,
                end_conversation,
                add_note,
                conversation_status,
                get_time_based_greeting,
                sofia_next_available_appointment,
                sofia_appointment_on_specific_day,
                sofia_smart_appointment_suggestions,
                sofia_get_todays_appointments,
                sofia_find_my_appointments_extended,
                book_appointment_calendar_system,  # NEW: Calendar integration booking
                emergency_prioritization,  # Emergency handling with pain scale
                phd_stomatology_first_aid_guidance  # PhD first aid guidance
            ],
        )
        self.should_end_conversation = False
    
    async def handle_response(self, response: str) -> str:
        """
        Processes the response and checks for conversation end signal
        CRITICAL: On end signal, end IMMEDIATELY!
        """
        # Prüfe auf Ende-Signal
        if "*[CALL_END_SIGNAL]*" in response:
            self.should_end_conversation = True
            logging.info("🔴 Conversation end signal detected - conversation ending IMMEDIATELY")
            # Remove the signal from the response
            response = response.replace("*[CALL_END_SIGNAL]*", "")
            
            # END IMMEDIATELY - no further messages!
            logging.info("🚨 CRITICAL: Conversation MUST end IMMEDIATELY!")
            
        # Prüfe auch den CallManager-Status
        if call_manager.is_conversation_ended():
            self.should_end_conversation = True
            logging.info("🔴 CallManager signals conversation end - ending IMMEDIATELY")
            
        return response
    
    def is_conversation_ended(self) -> bool:
        """
        Checks if the conversation should be ended
        """
        return self.should_end_conversation or call_manager.is_conversation_ended()


async def entrypoint(ctx: agents.JobContext):
    print("\n" + "!" * 60)
    print("!!! SOFIA ENTRYPOINT TRIGGERED !!!")
    print("!" * 60)
    print(f"Room: {ctx.room.name}")
    print(f"Room participants: {len(ctx.room.remote_participants)}")
    print("Starting English dental assistant with audio input...")
    logger.info("Starting English dental assistant agent")
    
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
    def on_track_published(publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        async def handle_track():
            await on_track_published_async(publication, participant)
        asyncio.create_task(handle_track())
    
    async def on_track_published_async(publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        print(f"Audio track detected: {publication.track_info.name}")
        logger.info(f"Audio track published: {publication.track_info.name}")
        
        if publication.track_info.kind == rtc.TrackKind.KIND_AUDIO:
            print("Microphone input active!")
            logger.info("Microphone input active")
            
            # Subscribe to the audio track
            track = await publication.track()
            if track:
                print("[MIC] Listening...")
                logger.info("Listening to audio track")
                
                # Start processing audio
                await session.process_track(track)
    
    ctx.room.on("track_published", on_track_published)
    
    def on_participant_connected(participant: rtc.RemoteParticipant):
        async def handle_participant():
            await on_participant_connected_async(participant)
        asyncio.create_task(handle_participant())
    
    async def on_participant_connected_async(participant: rtc.RemoteParticipant):
        print(f"Participant connected: {participant.identity}")
        logger.info(f"Participant connected: {participant.identity}")
    
    ctx.room.on("participant_connected", on_participant_connected)
    
    def on_data_received(data: rtc.DataPacket):
        async def handle_data():
            await on_data_received_async(data)
        asyncio.create_task(handle_data())
    
    async def on_data_received_async(data: rtc.DataPacket):
        print(f"Data received: {data.data}")
        logger.info(f"Data received: {data.data}")
    
    ctx.room.on("data_received", on_data_received)
    
    # Connect to the room
    await ctx.connect()
    print("Connected to LiveKit room")
    
    # Start the agent session
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=room_input_options,
    )
    
    print("Ready to listen! Please speak now...")
    logger.info("Agent ready to listen")
    
    # Generate initial greeting with AUTOMATIC date/time detection
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION + "\n\n**IMPORTANT**: Call `get_time_based_greeting()` IMMEDIATELY for automatic greeting!",
    )
    
    # NO automatic conversation end monitoring
    # Sofia runs continuously without interruptions
    
    # NO automatic monitoring - Sofia runs continuously
    
    # Wait for shutdown - WITHOUT automatic ending
    try:
        # Endless loop - Agent runs continuously
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Agent manually terminated")
    except Exception as e:
        logger.info(f"Agent error: {e}")
        # Keep running on errors
        await asyncio.sleep(5)
    finally:
        # Cleanup only on real shutdown
        print("Agent terminated")
        logger.info("Agent shutdown")


async def connect_to_room(room_name):
    """Direct connection to a specific room"""
    import os
    import requests
    import json
    
    print(f"DIRECT CONNECT TO ROOM: {room_name}")
    
    try:
        # Get token from the calendar server (same as web client does)
        response = requests.post('http://localhost:3005/api/sofia/connect', json={
            'participantName': f'Sofia-Agent-{room_name}',
            'roomName': room_name
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data['token']
            url = data['url']
            
            print(f"Got token for Sofia, connecting to {url}")
            
            # Create room and connect
            from livekit import rtc
            room = rtc.Room()
            
            await room.connect(url, token)
            print(f"SOFIA CONNECTED TO ROOM: {room_name}")
            
            # Create a fake JobContext for the entrypoint
            class FakeJobContext:
                def __init__(self, room):
                    self.room = room
                async def connect(self):
                    pass  # Already connected
            
            # Run the entrypoint
            ctx = FakeJobContext(room)
            await entrypoint(ctx)
            
        else:
            print(f"Failed to get token: {response.status_code}")
            
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    import sys
    import asyncio
    
    if len(sys.argv) > 1 and sys.argv[1] == "connect" and len(sys.argv) > 2:
        # Direct room connection mode
        room_name = sys.argv[2]
        print(f"Starting Sofia in direct connect mode for room: {room_name}")
        asyncio.run(connect_to_room(room_name))
    else:
        # Normal worker mode
        import os
        
        # Ensure environment variables are loaded
        load_dotenv()
        
        worker_options = agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            # Don't set agent_name to keep automatic dispatch enabled
            ws_url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
            api_secret=os.getenv("LIVEKIT_API_SECRET", "secret"),
        )
        
        print("\n" + "=" * 60)
        print("SOFIA DENTAL ASSISTANT - WORKER MODE")
        print("THIS IS THE REAL SOFIA FROM agent.py")
        print("=" * 60)
        print(f"LiveKit URL: {worker_options.ws_url}")
        print(f"API Key: {worker_options.api_key}")
        print("Auto-dispatch: ENABLED (no agent_name set)")
        print("Waiting for room assignments...")
        print("If you see 'SOFIA ENTRYPOINT TRIGGERED' below, Sofia is working!")
        print("=" * 60 + "\n")
        
        agents.cli.run_app(worker_options)
