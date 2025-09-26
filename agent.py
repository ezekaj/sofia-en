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
from src.agent.tools import (
    get_basic_info,
    get_time_based_greeting,
    get_current_datetime_info,
    end_conversation,
    general_help
)

load_dotenv()

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SofiaBaseAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",  # Female voice
                language="en-US",  # English language
                temperature=0.7,
            ),
            tools=[
                get_basic_info,
                get_time_based_greeting,
                get_current_datetime_info,
                end_conversation,
                general_help
            ],
        )
        self.should_end_conversation = False

    async def handle_response(self, response: str) -> str:
        """
        Processes the response and checks for conversation end signal
        """
        if "*[CALL_END_SIGNAL]*" in response:
            self.should_end_conversation = True
            logging.info("🔴 Conversation end signal detected - conversation ending")
            response = response.replace("*[CALL_END_SIGNAL]*", "")

        return response

    def is_conversation_ended(self) -> bool:
        """
        Checks if the conversation should be ended
        """
        return self.should_end_conversation


async def entrypoint(ctx: agents.JobContext):
    print("\n" + "!" * 60)
    print("!!! SOFIA BASE AGENT TRIGGERED !!!")
    print("!" * 60)
    print(f"Room: {ctx.room.name}")
    print(f"Room participants: {len(ctx.room.remote_participants)}")
    print("Starting Sofia base agent...")
    logger.info("Starting Sofia base agent")

    # Create the agent
    agent = SofiaBaseAgent()

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

    # Generate initial greeting
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION + "\n\n**IMPORTANT**: Call `get_time_based_greeting()` IMMEDIATELY for automatic greeting!",
    )

    # Wait for shutdown
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Agent manually terminated")
    except Exception as e:
        logger.info(f"Agent error: {e}")
        await asyncio.sleep(5)
    finally:
        print("Agent terminated")
        logger.info("Agent shutdown")


if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) > 1 and sys.argv[1] == "console":
        # Console mode
        print("\n" + "=" * 60)
        print("SOFIA BASE AGENT - CONSOLE MODE")
        print("GENERIC VOICE ASSISTANT")
        print("=" * 60)
        print("Console mode requested - Sofia will run in normal LiveKit mode")
        print("Connect via web interface or LiveKit client to interact")
        print("=" * 60 + "\n")

    # Ensure environment variables are loaded
    load_dotenv()

    worker_options = agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        ws_url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
        api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "secret"),
    )

    print("\n" + "=" * 60)
    print("SOFIA BASE AGENT - GENERIC VOICE ASSISTANT")
    print("=" * 60)
    print(f"LiveKit URL: {worker_options.ws_url}")
    print(f"API Key: {worker_options.api_key}")
    print("Auto-dispatch: ENABLED (no agent_name set)")
    print("Waiting for room assignments...")
    print("If you see 'SOFIA BASE AGENT TRIGGERED' below, Sofia is working!")
    print("=" * 60 + "\n")

    agents.cli.run_app(worker_options)