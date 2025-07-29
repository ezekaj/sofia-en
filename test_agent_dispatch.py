#!/usr/bin/env python3
"""
Test LiveKit Agent Dispatch Mechanism
This helps understand how agents are dispatched to rooms
"""
import asyncio
import logging
from livekit import api, rtc
import os
from dotenv import load_dotenv
import json

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_agent_dispatch():
    """Test how agent dispatch works"""
    
    # Create API client
    livekit_api = api.LiveKitAPI(
        os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
        os.getenv("LIVEKIT_API_KEY", "devkey"),
        os.getenv("LIVEKIT_API_SECRET", "secret")
    )
    
    # 1. List existing rooms
    print("\n📋 Checking existing rooms...")
    try:
        rooms = await livekit_api.room.list_rooms(api.ListRoomsRequest())
        print(f"Found {len(rooms.rooms)} rooms:")
        for room in rooms.rooms:
            print(f"  - {room.name} (participants: {room.num_participants})")
    except Exception as e:
        print(f"Error listing rooms: {e}")
    
    # 2. Create a test room with agent request metadata
    room_name = f"test-agent-room-{int(asyncio.get_event_loop().time())}"
    print(f"\n🏠 Creating room: {room_name}")
    
    try:
        # Create room with metadata that requests an agent
        room_metadata = json.dumps({
            "agent_request": True,
            "agent_type": "dental-receptionist"
        })
        
        created_room = await livekit_api.room.create_room(
            api.CreateRoomRequest(
                name=room_name,
                metadata=room_metadata
            )
        )
        print(f"✅ Room created: {created_room.name}")
        print(f"   Metadata: {created_room.metadata}")
    except Exception as e:
        print(f"❌ Error creating room: {e}")
        return
    
    # 3. Generate token for participant
    token = api.AccessToken(
        api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "secret")
    )
    
    participant_metadata = json.dumps({
        "type": "calendar-user",
        "request_agent": True
    })
    
    token.with_identity("test-participant").with_name("Test User")
    token.with_metadata(participant_metadata)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True
    ))
    
    jwt_token = token.to_jwt()
    print(f"\n🎫 Generated token for participant")
    
    # 4. Connect as participant
    room = rtc.Room()
    
    @room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        print(f"✅ Participant connected: {participant.identity}")
        print(f"   Metadata: {participant.metadata}")
        if "agent" in participant.identity.lower():
            print("🤖 AGENT DETECTED!")
    
    @room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        print(f"🎤 Track subscribed from {participant.identity}: {track.kind}")
    
    @room.on("data_received")
    def on_data_received(data: bytes, participant: rtc.RemoteParticipant):
        try:
            decoded = data.decode('utf-8')
            print(f"📨 Data from {participant.identity}: {decoded}")
        except:
            print(f"📨 Binary data from {participant.identity}: {len(data)} bytes")
    
    try:
        print(f"\n🔌 Connecting to room as participant...")
        await room.connect(
            os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            jwt_token
        )
        
        print(f"✅ Connected as: {room.local_participant.identity}")
        
        # List participants
        participants = list(room.remote_participants.values())
        print(f"\n👥 Participants in room: {len(participants)}")
        for p in participants:
            print(f"  - {p.identity} (metadata: {p.metadata})")
        
        # Send test data
        print("\n📤 Sending test data...")
        test_data = json.dumps({
            "type": "test",
            "message": "Hello from test participant"
        })
        await room.local_participant.publish_data(test_data.encode('utf-8'), reliable=True)
        
        # Wait for agent
        print("\n⏳ Waiting for agent to join (30 seconds)...")
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
    finally:
        await room.disconnect()
        print("\n🔌 Disconnected")
        
        # Clean up room
        try:
            await livekit_api.room.delete_room(api.DeleteRoomRequest(room=room_name))
            print(f"🗑️ Deleted test room: {room_name}")
        except:
            pass

if __name__ == "__main__":
    print("LiveKit Agent Dispatch Test")
    print("=" * 50)
    print("Make sure:")
    print("1. LiveKit server is running (docker-compose up livekit)")
    print("2. Sofia agent is running (python agent.py dev)")
    print("=" * 50)
    asyncio.run(test_agent_dispatch())