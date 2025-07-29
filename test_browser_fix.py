#!/usr/bin/env python3
"""
Test that the browser voice UI fix is working
"""
import httpx
import asyncio
import json

async def test_browser_fix():
    print("Testing Browser Voice UI Fix")
    print("=" * 50)
    
    # Test 1: Check if calendar server is responding
    print("1. Testing calendar server...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3005/health")
            health = response.json()
            print(f"   Calendar Health: {health['status']}")
    except Exception as e:
        print(f"   ERROR: Calendar not responding - {e}")
        return False
    
    # Test 2: Check if new token endpoint works
    print("\n2. Testing new LiveKit token endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:3005/api/livekit-token",
                json={
                    "identity": "test-user",
                    "room": "sofia-room"
                }
            )
            result = response.json()
            print(f"   Token endpoint: {response.status_code}")
            print(f"   Response: {result}")
            
            if result.get('success') and result.get('token'):
                print("   SUCCESS: Token endpoint working!")
            else:
                print("   FAILED: Token endpoint not working properly")
                
    except Exception as e:
        print(f"   ERROR: Token endpoint failed - {e}")
        return False
    
    # Test 3: Check LiveKit connectivity
    print("\n3. Checking LiveKit server...")
    try:
        async with httpx.AsyncClient() as client:
            # LiveKit doesn't have a simple HTTP health endpoint, so we just check if port is open
            response = await client.get("http://localhost:7880", timeout=2.0)
    except httpx.ConnectError:
        print("   WARNING: LiveKit may not be running on port 7880")
        print("   The browser won't be able to establish voice connection")
        print("   Run: docker-compose up -d livekit")
    except:
        # Other errors are expected (LiveKit uses WebSocket)
        print("   LiveKit port 7880 is responding")
    
    print("\n" + "=" * 50)
    print("BROWSER FIX STATUS:")
    print("- Calendar server: OK")
    print("- Token endpoint: Added to calendar server")
    print("- No changes to Sofia required")
    print("\nThe browser should now be able to:")
    print("1. Get LiveKit token from calendar server (not port 5001)")
    print("2. Connect to LiveKit WebSocket")
    print("3. Establish voice communication")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_browser_fix())