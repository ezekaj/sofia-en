import asyncio
import logging
from livekit import agents, rtc
from livekit.plugins import google
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleSofiaAgent:
    def __init__(self):
        self.name = "Sofia"
        print(f"SimpleSofiaAgent initialized")

async def entrypoint(ctx: agents.JobContext):
    """This gets called when a room needs an agent"""
    print(f"\n=== SOFIA AGENT ENTRYPOINT CALLED ===")
    print(f"Room name: {ctx.room.name}")
    print(f"Participant count: {len(ctx.room.remote_participants)}")
    
    # Connect to the room
    await ctx.connect()
    print(f"Connected to room: {ctx.room.name}")
    
    # List all participants
    for p in ctx.room.remote_participants.values():
        print(f"Participant in room: {p.identity}")
    
    # Create a simple agent
    agent = SimpleSofiaAgent()
    
    # Keep the agent alive
    print("Sofia agent is ready and listening...")
    
    try:
        # Keep running until disconnected
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Agent error: {e}")
    finally:
        print("Sofia agent shutting down")

if __name__ == "__main__":
    print("Starting Simple Sofia Agent Worker...")
    
    # Create worker options with explicit configuration
    worker_options = agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        ws_url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
        api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "secret"),
    )
    
    print(f"Worker configuration:")
    print(f"  URL: {worker_options.ws_url}")
    print(f"  API Key: {worker_options.api_key}")
    
    # Run the worker
    agents.cli.run_app(worker_options)