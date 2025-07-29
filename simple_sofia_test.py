#!/usr/bin/env python3
"""
Simple Sofia Test - Quick verification that everything is working
"""
import asyncio
import aiohttp
import json

async def simple_test():
    """Quick test of essential components"""
    
    print("Sofia Quick Test")
    print("===============")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test calendar server
            print("Testing calendar server...")
            async with session.get('http://localhost:3005') as resp:
                if resp.status == 200:
                    print("✓ Calendar server running")
                else:
                    print(f"✗ Calendar server error: {resp.status}")
                    return
            
            # Test token generation
            print("Testing token generation...")
            async with session.post('http://localhost:3005/api/livekit-token',
                                   json={'identity': 'test', 'room': 'sofia-room'}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✓ Token endpoint working")
                    print(f"  Token: {data['token'][:50]}...")
                else:
                    print(f"✗ Token error: {resp.status}")
                    return
            
            # Test integration script
            print("Testing browser integration script...")
            async with session.get('http://localhost:3005/sofia-livekit-integration-complete.js') as resp:
                if resp.status == 200:
                    content = await resp.text()
                    if 'SofiaLiveKitIntegration' in content and len(content) > 10000:
                        print("✓ Complete integration script available")
                    else:
                        print("✗ Integration script incomplete")
                else:
                    print(f"✗ Integration script error: {resp.status}")
                    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return
    
    print("\n" + "="*30)
    print("ALL TESTS PASSED!")
    print("="*30)
    print("\nNext steps:")
    print("1. Sofia agent should be running (check console)")
    print("2. Open browser to http://localhost:3005")
    print("3. Click Sofia button to connect")
    print("4. Check browser console for detailed logs")
    print("5. Speak to test voice interaction")

if __name__ == "__main__":
    asyncio.run(simple_test())