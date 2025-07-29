import asyncio
import os
from livekit import rtc
import requests
import time

async def test_fresh_room():
    """Test with a completely fresh room name"""
    
    # Use a unique room name with timestamp
    room_name = f"dental-room-{int(time.time())}"
    print(f"Creating fresh room: {room_name}")
    
    # Get token from server
    response = requests.post('http://localhost:3005/api/sofia/connect', json={
        'participantName': 'Test-User',
        'roomName': room_name
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data['token']
        url = data['url']
        
        print(f"Connecting to fresh room: {room_name}")
        
        # Connect to room
        room = rtc.Room()
        await room.connect(url, token)
        
        print(f"Connected! Room: {room.name}")
        print(f"Local participant: {room.local_participant.identity}")
        
        # Wait for Sofia to join
        print("\nWaiting for Sofia to join the fresh room...")
        for i in range(20):
            participants = [p.identity for p in room.remote_participants.values()]
            print(f"  Check {i+1}: Participants = {participants}")
            
            if participants:
                print(f"SOFIA JOINED! Participants: {participants}")
                break
                
            await asyncio.sleep(1)
        else:
            print("Sofia did not join after 20 seconds")
            
        await room.disconnect()
        print("Test completed")
    else:
        print(f"Failed to get token: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_fresh_room())