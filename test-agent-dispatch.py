import asyncio
import os
from livekit import api
import requests

async def test_agent_dispatch():
    """Test if agent dispatch works by creating a room with explicit agent request"""
    
    # Create a room using LiveKit API
    livekit_host = "http://localhost:7880"
    api_key = "devkey"
    api_secret = "secret"
    
    print("Testing LiveKit agent dispatch...")
    
    # Try to create a room with agent request
    room_name = "test-agent-room"
    
    # Method 1: Try using room creation API if available
    try:
        # Create room with agent metadata
        room_service = api.RoomService(livekit_host, api_key, api_secret)
        
        # Create room with metadata requesting agent
        room = await room_service.create_room(
            api.CreateRoomRequest(
                name=room_name,
                metadata="{\"agent_request\": true}"
            )
        )
        print(f"Room created: {room.name}")
    except Exception as e:
        print(f"Room creation via API failed: {e}")
    
    # Method 2: Join room and check if agent gets dispatched
    print("\nJoining room to trigger agent dispatch...")
    response = requests.post('http://localhost:3005/api/sofia/connect', json={
        'participantName': 'Dispatch-Test',
        'roomName': room_name
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"Got token for room: {room_name}")
        
        # Connect and wait
        from livekit import rtc
        room = rtc.Room()
        
        await room.connect(data['url'], data['token'])
        print(f"Connected to room: {room.name}")
        
        # Wait for agent
        print("\nWaiting for agent to join...")
        for i in range(15):
            participants = [p.identity for p in room.remote_participants.values()]
            print(f"  Check {i+1}: Participants = {participants}")
            
            if any('agent' in p.lower() or 'sofia' in p.lower() for p in participants):
                print("✅ AGENT JOINED!")
                break
                
            await asyncio.sleep(2)
        else:
            print("❌ Agent did not join after 30 seconds")
            
        await room.disconnect()
    
    print("\nTest completed")

if __name__ == "__main__":
    asyncio.run(test_agent_dispatch())