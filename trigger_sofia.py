#!/usr/bin/env python3
"""
Trigger Sofia to join sofia-room
"""
import requests
import json
import time

def trigger_sofia_agent():
    """Send a webhook to trigger Sofia agent to join the room"""
    
    # LiveKit webhook endpoint (agent should be listening)
    webhook_url = "http://localhost:8080/webhook"
    
    # Create a fake room created event
    webhook_data = {
        "event": "room_started",
        "room": {
            "sid": "RM_sofia_" + str(int(time.time())),
            "name": "sofia-room",
            "empty_timeout": 300,
            "creation_time": int(time.time()),
            "metadata": ""
        },
        "id": "EV_" + str(int(time.time())),
        "created_at": int(time.time())
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Sending webhook to trigger Sofia...")
        response = requests.post(webhook_url, json=webhook_data, headers=headers)
        
        if response.status_code == 200:
            print("✓ Webhook sent successfully!")
            print("Sofia should now join sofia-room")
        else:
            print(f"✗ Webhook failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to agent webhook endpoint")
        print("Make sure the agent is running with: python agent.py dev")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("Sofia Room Trigger")
    print("=" * 50)
    print()
    
    # Trigger the agent
    trigger_sofia_agent()
    
    print()
    print("Now check if Sofia appears in the debug window!")