# Sofia Voice Connection Debug Report

## Current Situation

### Working Components
1. **Sofia Agent (agent.py)**: Running on console with LiveKit agents framework
2. **LiveKit Server**: Running on ws://localhost:7880
3. **Browser Interface**: Can load and attempt to connect

### Identified Issues

## 1. Room Name Mismatch
**Issue**: The browser is trying to connect to `sofia-room` but the agent doesn't specify a room name
- Browser: `room: 'sofia-room'` (line 74 in sofia-livekit-integration.js)
- Agent: No explicit room name in the connection

## 2. Token Generation Issues
**Issue**: The browser is using a hardcoded test token that may not match the agent's expectations
- Browser token: Hardcoded JWT in generateTestToken() (line 277)
- Agent: Expects tokens from LiveKit server with proper room permissions

## 3. Missing LiveKit Client Reference
**Issue**: The browser code references `window.LivekitClient` but it should be `window.LivekitClient` (capital K)
- Line 32: `if (!window.LivekitClient)` should be `if (!window.LivekitClient)`
- Line 87-93: Uses `LivekitClient.Room` which should match the loaded SDK

## 4. Participant Identity Mismatch
**Issue**: The browser looks for participants with 'sofia' in their identity, but the agent may have a different identity
- Browser: Expects `participant.identity.includes('sofia')` (line 137)
- Agent: Identity is set by the LiveKit agents framework

## 5. Event Handler Gaps
**Issue**: The agent listens for specific events that may not match browser behavior
- Agent: Listens for `track_published` event (line 208)
- Browser: Publishes audio tracks differently

## 6. Missing Agent Context
**Issue**: The browser doesn't know which agent session to connect to
- Sofia runs as an agent worker, not a traditional participant
- The browser needs to connect to the correct agent session

## Solutions

### Solution 1: Fix Token Generation
The browser needs to get a proper token from the server that matches the agent's room:

```javascript
// In calendar server.js
app.post('/api/livekit-token', async (req, res) => {
    const { identity, room } = req.body;
    
    const at = new AccessToken('devkey', 'secret', {
        identity: identity,
        ttl: '1h',
    });
    
    at.addGrant({ 
        roomJoin: true, 
        room: room || 'agent-test-room',  // Match agent's room
        canPublish: true,
        canSubscribe: true,
        canPublishData: true,
    });
    
    res.json({ token: at.toJwt() });
});
```

### Solution 2: Fix LiveKit Client Reference
Update sofia-livekit-integration.js:
- Change `window.LivekitClient` to `window.LivekitClient` (check actual SDK object name)
- Or use the correct reference based on how the SDK is loaded

### Solution 3: Implement Proper Agent Connection
The browser needs to connect as a participant to the same room the agent is in:

```javascript
// Get the agent's room name from the server
const agentInfo = await fetch('/api/sofia-agent-info');
const { roomName } = await agentInfo.json();

// Connect to the same room
await this.room.connect(this.livekitUrl, this.token);
```

### Solution 4: Add Missing Event Handlers
The agent needs to handle browser participants properly:

```python
@ctx.room.on("participant_connected")
async def on_participant_connected(participant: rtc.RemoteParticipant):
    if "calendar" in participant.identity:
        # Handle calendar user connection
        await session.send_chat_message("Hallo! Ich bin Sofia...")
```

### Solution 5: Use LiveKit Agents Properly
The browser should connect as a regular participant, not try to be an agent:

1. Agent runs with `agents.cli.run_app()`
2. Browser connects as a normal participant to the same room
3. Agent handles the participant's audio/data

## Recommended Fix Order

1. **First**: Fix the LiveKit client reference in the browser
2. **Second**: Implement proper token generation on the server
3. **Third**: Ensure room names match between agent and browser
4. **Fourth**: Add proper participant handling in the agent
5. **Fifth**: Test audio flow between browser and agent

## Testing Steps

1. Start LiveKit server: `docker-compose up livekit`
2. Start Sofia agent: `python agent.py dev`
3. Start calendar server: `npm start`
4. Open browser and check console for errors
5. Click Sofia button and monitor both agent and browser logs

## Key Debug Commands

```bash
# Check LiveKit server logs
docker logs elo-deu-livekit-1

# Monitor agent logs
python agent.py dev 2>&1 | tee agent.log

# Check browser console
# Open DevTools and look for LiveKit connection errors
```

## Expected Behavior

1. Browser clicks Sofia button
2. Browser gets token and connects to LiveKit room
3. Agent receives participant_connected event
4. Browser publishes audio track
5. Agent subscribes to audio and processes speech
6. Agent responds with voice through its audio track
7. Browser receives and plays agent's audio

## Current Blocker

The main issue is that the browser and agent are not connecting to the same LiveKit room session. The agent is running as a worker that needs to be triggered to join a specific room, while the browser is trying to connect to a static room name.

## Next Steps

1. Review how the agent is started and which room it joins
2. Implement a coordination mechanism between browser and agent
3. Consider using LiveKit's agent dispatch mechanism
4. Test with the LiveKit playground to verify connection flow