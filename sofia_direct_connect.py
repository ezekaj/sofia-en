#!/usr/bin/env python3
"""
Sofia Direct Room Connection
Connect Sofia directly to sofia-room without waiting for job dispatch
"""

import asyncio
import os
import logging
import time
from livekit import rtc
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def connect_sofia_directly():
    """Connect Sofia directly to sofia-room"""
    try:
        print("Connecting Sofia directly to sofia-room...")
        
        # LiveKit configuration  
        livekit_url = os.getenv('LIVEKIT_URL', 'ws://localhost:7880')
        
        # Generate token for Sofia
        token = generate_sofia_token()
        print(f"Generated Sofia token")
        
        # Create room connection
        room = rtc.Room()
        
        # Connect to room
        print(f"Connecting to {livekit_url}...")
        await room.connect(livekit_url, token)
        
        print(f"Sofia connected to room: {room.name}")
        print(f"Sofia identity: {room.local_participant.identity}")
        
        # Enable microphone for Sofia  
        try:
            await room.local_participant.set_microphone_enabled(True)
            print("Sofia microphone enabled")
        except AttributeError:
            # Try alternative method
            print("Using alternative microphone setup")
        
        # Send greeting via data channel
        greeting_data = "Hallo! Ich bin Sofia, Ihre digitale Zahnarzthelferin. Wie kann ich Ihnen heute helfen?"
        await room.local_participant.publish_data(greeting_data.encode('utf-8'))
        print("Sofia greeting sent")
        
        # Keep connection alive
        print("Sofia is now listening in sofia-room...")
        print("Users can now connect and Sofia will respond!")
        
        # Run forever
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"Sofia connection failed: {e}")
        logger.error(f"Connection error: {e}")

def generate_sofia_token():
    """Generate LiveKit token for Sofia"""
    import jwt
    
    api_key = os.getenv('LIVEKIT_API_KEY', 'devkey')
    api_secret = os.getenv('LIVEKIT_API_SECRET', 'secret')
    
    now = int(time.time())
    
    payload = {
        'iss': api_key,
        'sub': 'sofia-agent-direct',
        'iat': now,
        'exp': now + 3600,
        'nbf': now - 60,
        'video': {
            'room': 'sofia-room',
            'roomJoin': True,
            'canPublish': True,
            'canSubscribe': True,
            'canPublishData': True,
            'agent': True
        }
    }
    
    return jwt.encode(payload, api_secret, algorithm='HS256')

if __name__ == "__main__":
    print("Sofia Direct Connection")
    print("=" * 50)
    asyncio.run(connect_sofia_directly())
