# Sofia Calendar Integration Guide

## Overview
This guide explains how Sofia (the German dental assistant) is integrated into the dental calendar system.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Dental Calendar │────▶│ Sofia LiveKit    │────▶│ Sofia Agent     │
│ (Browser UI)    │     │ Integration JS   │     │ (Python/LiveKit)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                                                  │
        │                                                  │
        ▼                                                  ▼
┌─────────────────┐                          ┌─────────────────┐
│ Calendar API    │                          │ Google Gemini   │
│ (Express/SQLite)│                          │ (AI Processing) │
└─────────────────┘                          └─────────────────┘
```

## Components

### 1. **Dental Calendar** (`dental-calendar/`)
- Web-based calendar interface
- Shows appointments and allows booking
- Integrates Sofia voice button
- Running on: http://localhost:3005

### 2. **Sofia LiveKit Integration** (`dental-calendar/public/sofia-livekit-integration.js`)
- Connects calendar to LiveKit server
- Handles WebRTC audio streams
- Manages voice conversations
- Sends/receives data to Sofia agent

### 3. **Sofia Agent** (`agent.py`)
- Main AI agent using LiveKit
- Processes German voice input
- Uses Google Gemini for understanding
- Manages appointment logic

### 4. **LiveKit Server**
- Real-time communication server
- Handles WebRTC connections
- Routes audio between browser and agent
- Running on: ws://localhost:7880

## How It Works

1. **User clicks Sofia button** in calendar
2. **Browser requests microphone** permission
3. **LiveKit connection** established to server
4. **User speaks** in German
5. **Audio sent** to Sofia agent via LiveKit
6. **Agent processes** with Google Gemini
7. **Response generated** and sent back
8. **Calendar updated** if appointment booked

## Starting the System

### Option 1: Use the batch file (Windows)
```batch
start_sofia_calendar.bat
```

### Option 2: Manual start
```bash
# Terminal 1 - Calendar
cd dental-calendar
npm start

# Terminal 2 - Sofia Web
python sofia_web.py

# Terminal 3 - LiveKit
docker-compose up livekit

# Terminal 4 - Sofia Agent
python agent.py dev
```

## Testing the Integration

1. Open http://localhost:3005
2. Click "Sofia Agent" button (top right)
3. Allow microphone access when prompted
4. Say: "Hallo Sofia"
5. Sofia should respond with greeting
6. Try: "Ich möchte einen Termin buchen"

## Common Voice Commands

- **"Hallo Sofia"** - Start conversation
- **"Ich möchte einen Termin buchen"** - Book appointment
- **"Welche Termine sind verfügbar?"** - Check availability
- **"Zeige meine Termine"** - Show my appointments
- **"Termin absagen"** - Cancel appointment
- **"Öffnungszeiten"** - Opening hours
- **"Auf Wiedersehen"** - End conversation

## Troubleshooting

### Sofia button doesn't work
1. Check all services are running
2. Check browser console for errors
3. Ensure microphone permissions granted
4. Try refreshing the page

### No voice response
1. Check LiveKit is running: `docker ps`
2. Check agent is running: Look for "Sofia Agent started"
3. Check browser supports WebRTC (Chrome/Edge recommended)

### Connection errors
1. Ensure ports are free: 3005, 5001, 7880
2. Check firewall settings
3. Try restarting all services

## Configuration

### Environment Variables (.env)
```
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
GOOGLE_API_KEY=your_key_here
```

### Calendar Settings
- Port: 3005 (configurable in server.js)
- Database: dental_calendar.db (SQLite)

### Sofia Settings
- Language: German (de-DE)
- Voice: Female (Aoede)
- Model: Google Gemini 1.5 Flash

## Development

### Adding New Commands
1. Edit `src/dental/dental_tools.py` - Add function
2. Edit `src/agent/prompts.py` - Update instructions
3. Edit `sofia-livekit-integration.js` - Handle UI actions

### Testing Changes
1. Restart Sofia agent after Python changes
2. Refresh browser after JS changes
3. Check logs in all terminals

## Security Notes

- Replace default LiveKit keys in production
- Use HTTPS in production
- Implement proper authentication
- Secure database access
- Validate all user inputs