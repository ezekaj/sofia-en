#!/usr/bin/env python3
"""
Complete Sofia Setup Test
Tests the entire pipeline: LiveKit → Sofia Agent → Calendar Server → Browser
"""
import asyncio
import aiohttp
import json
from livekit import api, rtc
import os
from dotenv import load_dotenv

load_dotenv('.env.development')

async def test_complete_setup():
    """Test all components of the Sofia system"""
    
    print("Complete Sofia Setup Test")
    print("=" * 50)
    
    # 1. Test LiveKit Server
    print("\n1. Testing LiveKit Server...")
    try:
        livekit_api = api.LiveKitAPI(
            os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            os.getenv("LIVEKIT_API_KEY", "devkey"),
            os.getenv("LIVEKIT_API_SECRET", "secret")
        )
        
        rooms = await livekit_api.room.list_rooms(api.ListRoomsRequest())
        print(f"LiveKit Server: OK - {len(rooms.rooms)} rooms found")
        
        # Check if sofia-room exists
        sofia_room = None
        for room in rooms.rooms:
            if room.name == 'sofia-room':
                sofia_room = room
                break
                
        if sofia_room:
            print(f"Sofia Room: OK - {sofia_room.num_participants} participants")
        else:
            print("Sofia Room: NOT FOUND")
            
    except Exception as e:
        print(f"LiveKit Server: ERROR - {e}")
        return False
    
    # 2. Test Calendar Server
    print("\n2. Testing Calendar Server...")
    try:
        async with aiohttp.ClientSession() as session:
            # Test basic health
            async with session.get('http://localhost:3005') as resp:
                if resp.status == 200:
                    print("Calendar Server: OK - HTTP 200")
                else:
                    print(f"Calendar Server: ERROR - HTTP {resp.status}")
                    return False
            
            # Test token endpoint
            async with session.post('http://localhost:3005/api/livekit-token', 
                                   json={'identity': 'test-user', 'room': 'sofia-room'}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("Token Endpoint: OK - Token generated")
                    print(f"Token length: {len(data.get('token', ''))}")
                else:
                    print(f"Token Endpoint: ERROR - HTTP {resp.status}")
                    
    except Exception as e:
        print(f"Calendar Server: ERROR - {e}")
        return False
    
    # 3. Test Room Connection (simulate browser)
    print("\n3. Testing Room Connection...")
    try:
        # Generate token like browser would
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:3005/api/livekit-token',
                                   json={
                                       'identity': 'test-browser-user',
                                       'room': 'sofia-room'
                                   }) as resp:
                token_data = await resp.json()
                token = token_data['token']
        
        # Connect to room like browser would
        room = rtc.Room()
        
        # Track events
        participants_connected = []
        tracks_received = []
        data_received = []
        
        @room.on("participant_connected")
        def on_participant_connected(participant):
            participants_connected.append(participant.identity)
            print(f"Participant connected: {participant.identity}")
            
            # Check if it's Sofia agent
            if 'sofia' in participant.identity.lower() or 'agent' in participant.identity.lower():
                print("SOFIA AGENT DETECTED!")
        
        @room.on("track_subscribed")
        def on_track_subscribed(track, publication, participant):
            tracks_received.append((track.kind, participant.identity))
            print(f"Track received: {track.kind} from {participant.identity}")
        
        @room.on("data_received")
        def on_data_received(payload, participant):
            try:
                data = json.loads(payload.decode('utf-8'))
                data_received.append(data)
                print(f"Data received: {data}")
            except:
                print(f"Binary data received from {participant.identity}")
        
        # Connect
        await room.connect(
            os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            token
        )
        
        print(f"Connected as: {room.local_participant.identity}")
        print(f"Room participants: {len(room.participants)}")
        
        # Enable microphone (simulating browser)
        await room.local_participant.setMicrophoneEnabled(True)
        print("Microphone enabled")
        
        # Send test message (like browser would)
        test_message = json.dumps({
            'type': 'user_ready',
            'message': 'Test browser user connected',
            'interface': 'test-browser'
        })
        await room.local_participant.publishData(test_message.encode('utf-8'), reliable=True)
        print("Test message sent")
        
        # Wait for responses
        print("Waiting for Sofia agent response...")
        await asyncio.sleep(10)
        
        # Report results
        print(f"\nResults:")
        print(f"Participants connected: {participants_connected}")
        print(f"Tracks received: {tracks_received}")
        print(f"Data messages: {len(data_received)}")
        
        # Cleanup
        await room.disconnect()
        print("Disconnected from room")
        
        # Check if Sofia agent was detected
        sofia_detected = any('sofia' in p.lower() or 'agent' in p.lower() 
                           for p in participants_connected)
        
        if sofia_detected:
            print("Connection Test: SUCCESS - Sofia agent detected")
        else:
            print("Connection Test: PARTIAL - No Sofia agent detected")
            
    except Exception as e:
        print(f"Room Connection: ERROR - {e}")
        return False
    
    # 4. Test Browser Integration
    print("\n4. Testing Browser Integration...")
    try:
        async with aiohttp.ClientSession() as session:
            # Check if the complete integration script is loaded
            async with session.get('http://localhost:3005/sofia-livekit-integration-complete.js') as resp:
                if resp.status == 200:
                    content = await resp.text()
                    if 'SofiaLiveKitIntegration' in content:
                        print("Browser Integration: OK - Complete script available")
                    else:
                        print("Browser Integration: ERROR - Script malformed")
                else:
                    print(f"Browser Integration: ERROR - HTTP {resp.status}")
                    
    except Exception as e:
        print(f"Browser Integration: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("SETUP TEST COMPLETE")
    print("=" * 50)
    print("\nTo test in browser:")
    print("1. Open http://localhost:3005")
    print("2. Click the Sofia button")
    print("3. Check browser console for connection messages")
    print("4. Speak to test voice interaction")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_complete_setup())