#!/usr/bin/env python3
"""
Test script for the German dental assistant agent with audio capabilities
"""
import asyncio
import os
from livekit import api
from dotenv import load_dotenv

load_dotenv()

async def test_audio_connection():
    """Test audio connection to the LiveKit room"""
    print("🧪 Teste Audio-Verbindung...")
    
    # Get credentials from environment
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not all([url, api_key, api_secret]):
        print("❌ Fehlende LiveKit-Credentials!")
        return
    
    # Create a test room service
    room_service = api.room_service.RoomService(url, api_key, api_secret)
    
    try:
        # List active rooms
        rooms = await room_service.list_rooms()
        print(f"📋 Aktive Räume: {len(rooms.rooms)}")
        
        for room in rooms.rooms:
            print(f"  - {room.name} ({room.num_participants} Teilnehmer)")
            
            # List participants in the room
            participants = await room_service.list_participants(room.name)
            for participant in participants.participants:
                print(f"    👤 {participant.identity} - {participant.state}")
                
                # Check for audio tracks
                for track in participant.tracks:
                    if track.type == api.TrackType.AUDIO:
                        print(f"      🎵 Audio-Track: {track.name}")
    
    except Exception as e:
        print(f"❌ Fehler: {e}")

async def create_test_room():
    """Create a test room for audio testing"""
    print("🏗️ Erstelle Test-Raum...")
    
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    room_service = api.room_service.RoomService(url, api_key, api_secret)
    
    try:
        # Create a test room
        room = await room_service.create_room("dental-test", config=api.RoomConfiguration(
            max_participants=5,
            empty_timeout=60,  # 1 minute timeout
        ))
        print(f"✅ Test-Raum erstellt: {room.name}")
        
        # Generate access token for testing
        token = api.AccessToken(api_key, api_secret)
        token.with_identity("test-user")
        token.with_name("Test User")
        token.with_grants(api.VideoGrants(
            room_join=True,
            room="dental-test",
            can_publish=True,
            can_subscribe=True,
        ))
        
        access_token = token.to_jwt()
        print(f"🔑 Access Token: {access_token[:50]}...")
        
        print(f"🌐 Verbinden Sie sich mit: {url}")
        print(f"📋 Raum: dental-test")
        print(f"🎫 Token: {access_token}")
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Raums: {e}")

if __name__ == "__main__":
    print("=== Audio-Test für Deutsche Zahnarzt-Assistentin ===")
    asyncio.run(test_audio_connection())
    print("\n" + "="*50 + "\n")
    asyncio.run(create_test_room())
