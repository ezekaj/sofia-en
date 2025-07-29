# Quick Deployment Guide for Sofia AI Voice Mode

## Overview
This guide provides a simplified deployment solution that can be implemented within hours for investor demos. The solution uses managed services to minimize complexity while maintaining reliability.

## Architecture

### Simplified Stack
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Web Client    │────▶│  LiveKit Cloud   │────▶│   Railway.app   │
│  (Browser/App)  │     │  (Managed SFU)   │     │  (Sofia Agent)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                 │                         │
                                 │                         ▼
                                 │                 ┌─────────────────┐
                                 └────────────────▶│   Railway.app   │
                                                   │(Calendar Backend)│
                                                   └─────────────────┘
```

## Service Selection

### 1. **LiveKit Cloud** (Managed WebRTC)
- No server management required
- Auto-scaling built-in
- $0.006/minute per participant
- Free tier: 1000 minutes/month

### 2. **Railway.app** (Application Hosting)
- One-click deployments
- Built-in logging and monitoring
- Automatic HTTPS
- $5/month per service + usage

### 3. **Neon Database** (Managed PostgreSQL)
- Serverless Postgres
- Auto-scaling
- Free tier: 3GB storage
- Better than SQLite for production

## Quick Deployment Steps

### Step 1: Set Up LiveKit Cloud (10 minutes)

1. Sign up at https://cloud.livekit.io
2. Create a new project
3. Get your credentials:
   - API Key
   - API Secret
   - WebSocket URL (wss://your-project.livekit.cloud)

### Step 2: Prepare Your Code (20 minutes)

Create deployment-ready configurations:

**1. Create `railway.json` for Sofia Agent:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python agent.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**2. Create `Dockerfile.sofia` (alternative to railway.json):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose health check port
EXPOSE 8080

# Start the agent
CMD ["python", "agent.py"]
```

**3. Update environment variables for production:**
```env
# Production environment variables
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
GOOGLE_API_KEY=your-google-api-key
CALENDAR_URL=https://your-calendar.railway.app
LOG_LEVEL=INFO
PYTHON_ENV=production
```

### Step 3: Deploy Sofia Agent to Railway (15 minutes)

1. Sign up at https://railway.app
2. Install Railway CLI: `npm install -g @railway/cli`
3. Deploy Sofia:
```bash
cd elo-deu
railway login
railway init
railway up
railway domain  # Get your public URL
```

### Step 4: Deploy Calendar Backend (15 minutes)

**1. Create `Dockerfile.calendar`:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY dental-calendar/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY dental-calendar/ ./

# Expose port
EXPOSE 3005

# Start server
CMD ["npm", "start"]
```

**2. Deploy to Railway:**
```bash
cd dental-calendar
railway init
railway up
railway domain
```

### Step 5: Configure Services (10 minutes)

**1. Set Railway environment variables:**
```bash
# For Sofia Agent
railway variables set LIVEKIT_URL=wss://your-project.livekit.cloud
railway variables set LIVEKIT_API_KEY=your-key
railway variables set LIVEKIT_API_SECRET=your-secret
railway variables set GOOGLE_API_KEY=your-google-key
railway variables set CALENDAR_URL=https://calendar.railway.app

# For Calendar Backend
railway variables set DATABASE_URL=postgres://...
railway variables set JWT_SECRET=your-jwt-secret
railway variables set CORS_ORIGIN=https://your-frontend.com
```

### Step 6: Create Simple Demo Frontend (30 minutes)

Create `demo.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Sofia AI - Dental Assistant Demo</title>
    <script src="https://unpkg.com/livekit-client/dist/livekit-client.umd.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .connected { background: #d4edda; }
        .disconnected { background: #f8d7da; }
        button {
            padding: 15px 30px;
            font-size: 18px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; }
    </style>
</head>
<body>
    <h1>Sofia AI - Dental Assistant Demo</h1>
    <div id="status" class="status disconnected">Disconnected</div>
    <button id="connect" onclick="connectToSofia()">Talk to Sofia</button>
    <button id="disconnect" onclick="disconnect()" disabled>End Call</button>
    
    <div id="logs" style="margin-top: 20px; padding: 10px; background: #f5f5f5; border-radius: 5px;">
        <h3>Activity Log</h3>
        <div id="logContent"></div>
    </div>

    <script>
        let room;
        let localParticipant;
        
        function log(message) {
            const logContent = document.getElementById('logContent');
            const timestamp = new Date().toLocaleTimeString();
            logContent.innerHTML += `<div>[${timestamp}] ${message}</div>`;
            logContent.scrollTop = logContent.scrollHeight;
        }
        
        async function connectToSofia() {
            try {
                log('Requesting microphone access...');
                
                // Get access token from your backend
                const response = await fetch('https://your-backend.railway.app/api/livekit-token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        identity: 'demo-user-' + Date.now(),
                        room: 'sofia-room'
                    })
                });
                
                const { token } = await response.json();
                
                log('Connecting to Sofia...');
                
                // Connect to LiveKit room
                room = new LiveKit.Room({
                    adaptiveStream: true,
                    dynacast: true,
                });
                
                await room.connect('wss://your-project.livekit.cloud', token);
                
                log('Connected! You can now speak with Sofia.');
                
                // Update UI
                document.getElementById('status').className = 'status connected';
                document.getElementById('status').textContent = 'Connected to Sofia';
                document.getElementById('connect').disabled = true;
                document.getElementById('disconnect').disabled = false;
                
                // Publish microphone
                await room.localParticipant.setMicrophoneEnabled(true);
                log('Microphone enabled. Say "Hallo" to start!');
                
                // Listen for Sofia's audio
                room.on('trackSubscribed', (track, publication, participant) => {
                    if (track.kind === 'audio') {
                        track.attach();
                        log('Sofia is ready to speak');
                    }
                });
                
            } catch (error) {
                log('Error: ' + error.message);
                console.error(error);
            }
        }
        
        async function disconnect() {
            if (room) {
                await room.disconnect();
                log('Disconnected from Sofia');
                
                // Update UI
                document.getElementById('status').className = 'status disconnected';
                document.getElementById('status').textContent = 'Disconnected';
                document.getElementById('connect').disabled = false;
                document.getElementById('disconnect').disabled = true;
            }
        }
    </script>
</body>
</html>
```

## Essential Configuration

### 1. **Health Checks**
Sofia agent already includes health check endpoint on port 8080.

### 2. **Logging Configuration**
Add structured logging for production:

```python
# Add to agent.py
import structlog

logger = structlog.get_logger()

# Log important events
logger.info("agent_started", room=room_name, timestamp=datetime.now())
logger.info("appointment_booked", patient=patient_name, date=appointment_date)
```

### 3. **Error Handling**
Already included in the agent with retry logic and circuit breakers.

## Monitoring & Troubleshooting

### 1. **Railway Dashboard**
- Real-time logs
- CPU/Memory usage
- Request metrics
- Deployment history

### 2. **LiveKit Dashboard**
- Active rooms
- Participant count
- Bandwidth usage
- Connection quality

### 3. **Quick Troubleshooting**
```bash
# Check logs
railway logs

# Restart service
railway restart

# Check environment variables
railway variables

# Scale up if needed
railway scale --min=2 --max=5
```

## Cost Estimates

### Monthly Costs (10-20 concurrent users)
- **LiveKit Cloud**: ~$50-100 (based on usage)
- **Railway (2 services)**: $10 + usage (~$20-30)
- **Neon Database**: Free tier or $19/month
- **Total**: ~$80-150/month

### Demo/Pilot Costs (low usage)
- **LiveKit Cloud**: Free tier (1000 minutes)
- **Railway**: $10 + minimal usage
- **Neon Database**: Free tier
- **Total**: ~$15-25/month

## Quick Start Checklist

- [ ] Sign up for LiveKit Cloud
- [ ] Sign up for Railway
- [ ] Clone your repository
- [ ] Update environment variables
- [ ] Deploy Sofia agent
- [ ] Deploy Calendar backend
- [ ] Test with demo frontend
- [ ] Configure custom domain (optional)

## Time Estimate
- Total deployment time: 1-2 hours
- Prerequisites setup: 30 minutes
- Service deployment: 45 minutes
- Testing & verification: 30 minutes

## Next Steps
1. Deploy the services following this guide
2. Test with the demo frontend
3. Monitor initial performance
4. Scale as needed for the demo