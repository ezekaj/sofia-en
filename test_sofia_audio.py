#!/usr/bin/env python3
"""
Test Sofia Audio Connection
Prüft ob Sofia richtig Audio sendet und empfängt
"""

import asyncio
from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

async def check_sofia_room():
    """Check Sofia room and participants"""
    
    # LiveKit server details
    url = "http://localhost:7880"
    api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
    api_secret = os.getenv("LIVEKIT_API_SECRET", "secret")
    
    # Create API client
    lk_api = api.LiveKitAPI(url, api_key, api_secret)
    
    try:
        # List all rooms
        print("Checking LiveKit rooms...")
        rooms = await lk_api.room.list_rooms()
        
        if not rooms:
            print("No active rooms found!")
            return
            
        for room in rooms:
            print(f"\nRoom: {room.name}")
            print(f"  Created: {room.creation_time}")
            print(f"  Participants: {room.num_participants}")
            
            # List participants in room
            participants = await lk_api.room.list_participants(room.name)
            for p in participants:
                print(f"\n  Participant: {p.identity}")
                print(f"    State: {p.state}")
                print(f"    Joined: {p.joined_at}")
                print(f"    Audio tracks: {len([t for t in p.tracks if t.type == 'AUDIO'])}")
                
                # Check tracks
                for track in p.tracks:
                    print(f"    Track: {track.sid} - Type: {track.type}, Muted: {track.muted}")
    
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure LiveKit server is running on http://localhost:7880")

async def create_test_token():
    """Create a test token to join Sofia's room"""
    from livekit import api
    
    token = api.AccessToken(
        api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "secret")
    )
    
    token.with_identity("test-audio-user").with_name("Test User")
    token.with_grants(api.VideoGrants(
        room_join=True,
        room="sofia-room",
        can_publish=True,
        can_subscribe=True
    ))
    
    jwt = token.to_jwt()
    print(f"\nTest token for 'sofia-room':")
    print(jwt)
    
    return jwt

if __name__ == "__main__":
    print("Sofia Audio Connection Test")
    print("=" * 50)
    
    # Check rooms and participants
    asyncio.run(check_sofia_room())
    
    # Generate test token
    print("\n" + "=" * 50)
    asyncio.run(create_test_token())