#!/usr/bin/env python3
"""
Simple Sofia Test - Direct Room Connection
"""
import asyncio
import logging
from livekit import api, rtc
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_sofia_connection():
    """Test direct connection to sofia-room"""
    
    # Create a test participant
    room = rtc.Room()
    
    # Generate token for sofia-room
    token = api.AccessToken(
        api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "secret")
    )
    
    token.with_identity("sofia-test-agent").with_name("Sofia Test")
    token.with_grants(api.VideoGrants(
        room_join=True,
        room="sofia-room",
        can_publish=True,
        can_subscribe=True
    ))
    
    jwt_token = token.to_jwt()
    
    @room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        print(f"✅ Participant connected: {participant.identity}")
    
    @room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        print(f"🎤 Track subscribed from {participant.identity}: {track.kind}")
    
    @room.on("connection_state_changed")
    def on_connection_state_changed(state: rtc.ConnectionState):
        print(f"📡 Connection state: {state}")
    
    try:
        print("🔄 Connecting to sofia-room...")
        await room.connect(
            os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            jwt_token
        )
        
        print(f"✅ Connected as: {room.local_participant.identity}")
        print(f"📍 Room: {room.name}")
        
        # List current participants
        participants = list(room.remote_participants.values())
        print(f"👥 Participants in room: {len(participants)}")
        for p in participants:
            print(f"  - {p.identity}")
        
        # Wait and listen
        print("\n⏳ Waiting for other participants...")
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await room.disconnect()
        print("🔌 Disconnected")

if __name__ == "__main__":
    print("Sofia Connection Test")
    print("=" * 50)
    asyncio.run(test_sofia_connection())