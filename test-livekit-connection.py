import asyncio
import os
from livekit import rtc
import requests

async def test_connection():
    """Test if we can connect to LiveKit and see participants"""
    
    # Get a token from the server
    print("Getting token from server...")
    response = requests.post('http://localhost:3005/api/sofia/connect', json={
        'participantName': 'Test-Client',
        'roomName': 'dental-calendar'
    })
    
    if response.status_code != 200:
        print(f"Failed to get token: {response.status_code}")
        return
        
    data = response.json()
    token = data['token']
    url = data['url']
    
    print(f"Got token, connecting to {url}")
    
    # Create room and connect
    room = rtc.Room()
    
    # Add event handlers
    def on_participant_connected(participant):
        print(f"Participant connected: {participant.identity}")
        
    def on_participant_disconnected(participant):
        print(f"Participant disconnected: {participant.identity}")
        
    room.on("participant_connected", on_participant_connected)
    room.on("participant_disconnected", on_participant_disconnected)
    
    # Connect to room
    await room.connect(url, token)
    print(f"Connected to room: {room.name}")
    print(f"Local participant: {room.local_participant.identity}")
    print(f"Remote participants: {[p.identity for p in room.remote_participants.values()]}")
    
    # Wait and check for participants periodically
    for i in range(10):
        await asyncio.sleep(2)
        print(f"\nCheck {i+1}:")
        print(f"  Remote participants: {[p.identity for p in room.remote_participants.values()]}")
        
    await room.disconnect()
    print("Test completed")

if __name__ == "__main__":
    asyncio.run(test_connection())