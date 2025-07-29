#!/usr/bin/env python3
"""
Sofia Room Creator - Ensures the sofia-room exists for browser connection
This should be run before starting the Sofia agent
"""
import asyncio
import logging
from livekit import api
import os
from dotenv import load_dotenv
import subprocess
import sys

load_dotenv('.env.development')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_sofia_room():
    """Create the sofia-room if it doesn't exist"""
    
    # Create API client
    livekit_api = api.LiveKitAPI(
        os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
        os.getenv("LIVEKIT_API_KEY", "devkey"),
        os.getenv("LIVEKIT_API_SECRET", "secret")
    )
    
    try:
        # Try to create the room
        room_name = "sofia-room"
        
        print(f"Creating room: {room_name}")
        await livekit_api.room.create_room(
            api.CreateRoomRequest(
                name=room_name,
                metadata=json.dumps({
                    "type": "dental-receptionist",
                    "created_by": "room_creator",
                    "timestamp": datetime.now().isoformat()
                })
            )
        )
        print(f"Room '{room_name}' created successfully")
        
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"Room '{room_name}' already exists")
        else:
            print(f"Error creating room: {e}")
            return False
    
    # List existing rooms
    try:
        print("\nListing existing rooms...")
        rooms = await livekit_api.room.list_rooms(api.ListRoomsRequest())
        print(f"Found {len(rooms.rooms)} rooms:")
        for room in rooms.rooms:
            print(f"  - {room.name} (participants: {room.num_participants})")
    except Exception as e:
        print(f"Error listing rooms: {e}")
    
    return True

async def start_sofia_with_room():
    """Create room and start Sofia agent"""
    
    print("Sofia Room Creator & Agent Starter")
    print("=" * 50)
    
    # First create the room
    success = await create_sofia_room()
    if not success:
        print("Failed to create room, exiting")
        return
    
    # Wait a moment for room to be ready
    await asyncio.sleep(2)
    
    # Check if we should start the agent
    if len(sys.argv) > 1 and sys.argv[1] == "agent":
        print("\nStarting Sofia agent...")
        try:
            # Start the agent in a subprocess
            process = subprocess.Popen(
                [sys.executable, "agent.py", "dev"],
                cwd=os.getcwd()
            )
            
            print(f"Sofia agent started with PID: {process.pid}")
            print("Agent is now running and will connect to sofia-room")
            print("You can now use the browser interface to connect")
            
            # Wait for the process or handle Ctrl+C
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\nStopping Sofia agent...")
                process.terminate()
                process.wait()
                print("Sofia agent stopped")
                
        except Exception as e:
            print(f"Error starting agent: {e}")
    else:
        print("\nRoom is ready!")
        print("To start Sofia agent, run: python start_sofia_room.py agent")
        print("You can now connect via browser")

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    asyncio.run(start_sofia_with_room())