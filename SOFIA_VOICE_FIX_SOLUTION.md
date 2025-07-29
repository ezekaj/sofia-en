# Sofia Voice Connection Fix Solution

## Root Cause Analysis

The issue is that **LiveKit Agents work differently than regular LiveKit participants**:

1. **Agent Mode**: Sofia runs as a LiveKit Agent Worker, not a regular participant
2. **Room Creation**: Agents don't join pre-existing rooms; they create rooms when dispatched
3. **Token Mismatch**: The browser is using a static token for a room that doesn't exist yet

## How LiveKit Agents Actually Work

1. Agent starts and registers with LiveKit server as available worker
2. When a participant joins a room with specific metadata, LiveKit dispatches an agent
3. The agent then joins that room and handles the participant

## The Fix: Proper Agent Dispatch

### Step 1: Update Browser Token Generation

The browser needs to request agent dispatch when joining:

```javascript
// In sofia-livekit-integration.js, update the connect method:
async connect() {
    try {
        this.updateUI('connecting', '🔄 Verbinde mit Sofia...');
        
        // Create a unique room name for this session
        const roomName = 'sofia-session-' + Date.now();
        
        // Get token with agent dispatch metadata
        const tokenResponse = await fetch('/api/livekit-token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                identity: 'calendar-user-' + Date.now(),
                room: roomName,
                metadata: JSON.stringify({
                    agent_request: true,
                    agent_type: 'dental-receptionist'
                })
            })
        });
        
        // ... rest of connection code
    } catch (error) {
        console.error('Connection error:', error);
        this.handleError('Verbindung fehlgeschlagen: ' + error.message);
    }
}
```

### Step 2: Update Calendar Server Token Generation

```javascript
// In server.js, add proper token endpoint:
app.post('/api/livekit-token', async (req, res) => {
    try {
        const { identity, room, metadata } = req.body;
        
        const AccessToken = require('livekit-server-sdk').AccessToken;
        const token = new AccessToken('devkey', 'secret', {
            identity: identity,
            ttl: '1h',
            metadata: metadata || ''
        });
        
        token.addGrant({ 
            roomJoin: true, 
            room: room,
            canPublish: true,
            canSubscribe: true,
            canPublishData: true
        });
        
        res.json({ 
            token: token.toJwt(),
            room: room,
            ws_url: 'ws://localhost:7880'
        });
    } catch (error) {
        console.error('Token generation error:', error);
        res.status(500).json({ error: 'Failed to generate token' });
    }
});
```

### Step 3: Fix LiveKit Client Reference

In sofia-livekit-integration.js, fix the client reference:

```javascript
// Line 32 - Check the correct global object name
if (!window.LivekitClient) {
    // Try alternative names
    if (window.LiveKit) {
        window.LivekitClient = window.LiveKit;
    } else if (window.livekitClient) {
        window.LivekitClient = window.livekitClient;
    } else {
        throw new Error('LiveKit Client not loaded - check script tag');
    }
}

// Use the correct constructors
this.room = new LivekitClient.Room({
    adaptiveStream: true,
    dynacast: true
});
```

### Step 4: Agent Configuration Update

The agent needs to handle room assignment properly:

```python
# In agent.py, the entrypoint function should handle the room properly
async def entrypoint(ctx: agents.JobContext):
    # The ctx already contains the room that was created for this job
    print(f"Agent dispatched to room: {ctx.room.name}")
    
    # ... rest of the agent code
```

## Alternative Solution: Direct Room Mode

If agent dispatch is too complex, use direct room mode:

### Option 1: Start Agent in Specific Room

```bash
# Start agent with specific room
python agent.py dev --room sofia-room
```

### Option 2: Create Simple WebSocket Bridge

Create a simpler connection that doesn't use agent dispatch:

```python
# sofia_web_bridge.py
from livekit import api, rtc
import asyncio
import websockets

async def create_sofia_room():
    """Create a persistent room for Sofia"""
    room_service = api.RoomService(
        'ws://localhost:7880',
        'devkey',
        'secret'
    )
    
    # Create room
    await room_service.create_room(
        api.CreateRoomRequest(name='sofia-room')
    )
    
    # Start Sofia in this room
    # ... agent connection code
```

## Recommended Quick Fix

1. **Use the test token but fix the SDK reference**:

```javascript
// In sofia-livekit-integration.js
async initialize() {
    console.log('🎤 Initializing Sofia LiveKit Integration...');
    
    try {
        // Fix SDK reference
        if (window.LiveKit) {
            window.LivekitClient = window.LiveKit;
        }
        
        if (!window.LivekitClient) {
            throw new Error('LiveKit Client not loaded');
        }
        
        console.log('✅ Sofia LiveKit Integration ready!');
        return true;
        
    } catch (error) {
        console.error('❌ Failed to initialize:', error);
        return false;
    }
}
```

2. **Start a test room creator alongside the agent**:

```python
# start_sofia_with_room.py
import asyncio
from livekit import api
import subprocess
import os

async def setup_room():
    # Create API client
    livekit_api = api.LiveKitAPI(
        'ws://localhost:7880',
        'devkey',
        'secret'
    )
    
    # Create room
    await livekit_api.room.create_room(
        api.CreateRoomRequest(name='sofia-room')
    )
    
    print("Room 'sofia-room' created")
    
    # Start agent
    subprocess.Popen(['python', 'agent.py', 'dev'])

if __name__ == "__main__":
    asyncio.run(setup_room())
```

## Testing Steps

1. Fix the LiveKit client reference in the browser code
2. Ensure the agent is running (`python agent.py dev`)
3. Open browser console and check for `window.LiveKit` or `window.LivekitClient`
4. Click the Sofia button and monitor both consoles

## Expected Console Output

**Browser Console:**
```
🎤 Initializing Sofia LiveKit Integration...
✅ Sofia LiveKit Integration ready!
🔄 Verbinde mit Sofia...
✅ Connected to room
```

**Agent Console:**
```
Agent dispatched to room: sofia-room
Teilnehmer verbunden: calendar-user-xxxxx
Audio-Track erkannt: microphone
```

## Quick Debug Commands

```javascript
// In browser console, check LiveKit SDK:
console.log(window.LiveKit);
console.log(window.LivekitClient);
console.log(window.livekit);

// Check if room exists:
fetch('/api/livekit-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        identity: 'test-user',
        room: 'sofia-room'
    })
}).then(r => r.json()).then(console.log);
```

The main issue is coordinating between the agent worker model and direct room connections. The quickest fix is to ensure the SDK is properly loaded and referenced in the browser.