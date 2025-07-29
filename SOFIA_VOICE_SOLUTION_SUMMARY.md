# Sofia Voice Connection Solution Summary

## Problem Summary

The voice connection between Sofia agent and the browser isn't working because:

1. **LiveKit SDK Reference Error**: The browser code references `window.LivekitClient` (capital K) but the SDK exports as `window.LivekitClient` (lowercase k)
2. **Room Connection Model**: LiveKit agents use a worker dispatch model, not direct room connections
3. **Token/Room Mismatch**: The browser tries to connect to a static room that may not exist

## Immediate Fix (Quick Solution)

### 1. Update the HTML to use the fixed integration script:

```html
<!-- In index.html, replace: -->
<script src="sofia-livekit-integration.js"></script>
<!-- With: -->
<script src="sofia-livekit-integration-fixed.js"></script>
```

### 2. Or apply this minimal fix to the existing file:

```javascript
// In sofia-livekit-integration.js, line 32:
// Replace:
if (!window.LivekitClient) {

// With:
if (!window.LivekitClient) {

// And line 87-93, replace all instances of LivekitClient with LivekitClient
```

### 3. Start a Room Creator alongside the agent:

Create `start_sofia_room.py`:
```python
import asyncio
from livekit import api
import subprocess

async def create_room_and_start_agent():
    # Create the room first
    livekit_api = api.LiveKitAPI(
        "ws://localhost:7880",
        "devkey",
        "secret"
    )
    
    try:
        await livekit_api.room.create_room(
            api.CreateRoomRequest(name="agent-test-room")
        )
        print("✅ Room 'agent-test-room' created")
    except:
        print("Room already exists")
    
    # Now the agent can be started
    print("Starting Sofia agent...")
    subprocess.run(["python", "agent.py", "dev"])

if __name__ == "__main__":
    asyncio.run(create_room_and_start_agent())
```

## Complete Fix (Proper Agent Dispatch)

### Understanding LiveKit Agents

LiveKit agents work differently than regular participants:
1. Agent starts and registers as available worker
2. When a participant joins a room with specific metadata, LiveKit dispatches an agent
3. The agent then joins that specific room

### To implement proper agent dispatch:

1. **Update the browser to request agent dispatch**:
```javascript
// In connect() method:
const roomName = 'sofia-session-' + Date.now();
const metadata = JSON.stringify({
    agent_request: true,
    agent_type: 'dental-receptionist'
});
```

2. **Configure agent to handle dispatch requests**:
The current agent.py is already set up correctly with `agents.cli.run_app()`

3. **Ensure LiveKit server has agent dispatch enabled**:
Check `livekit.yaml` for agent configuration

## Testing Steps

### Quick Test (Direct Room):
```bash
# Terminal 1: Start LiveKit
docker-compose up livekit

# Terminal 2: Create room and start agent
python start_sofia_room.py

# Terminal 3: Start calendar server
cd dental-calendar && npm start

# Browser: Open calendar and click Sofia button
```

### Debug in Browser Console:
```javascript
// Check SDK is loaded
console.log(window.LivekitClient);

// Check room connection
if (window.sofiaLiveKit) {
    console.log('Connected:', window.sofiaLiveKit.isConnected);
    console.log('Room:', window.sofiaLiveKit.room);
}
```

## Key Files Modified/Created

1. `sofia-livekit-integration-fixed.js` - Fixed SDK reference
2. `test_agent_dispatch.py` - Test agent dispatch mechanism
3. `SOFIA_VOICE_DEBUG_REPORT.md` - Detailed debug analysis
4. `SOFIA_VOICE_FIX_SOLUTION.md` - Complete fix guide

## Expected Behavior When Fixed

1. Click Sofia button in browser
2. Browser connects to LiveKit room
3. Agent receives notification and joins same room
4. Browser microphone → Agent processes speech → Agent responds with voice
5. Two-way voice conversation works

## Common Issues and Solutions

### "LiveKit Client not loaded"
- Check browser console for errors loading the SDK
- Verify the script tag URL is correct
- Check if LivekitClient (lowercase k) exists in window

### "Agent not responding"
- Verify agent is running: `python agent.py dev`
- Check agent logs for connection attempts
- Ensure room names match between browser and agent

### "No audio"
- Check browser permissions for microphone
- Verify audio tracks are being published/subscribed
- Look for audio elements in DOM

## Next Steps

1. Apply the minimal fix to get it working quickly
2. Test the connection
3. Once working, implement proper agent dispatch for production
4. Add error handling and reconnection logic