# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ELO German - A sophisticated German dental practice AI voice assistant built with LiveKit, Google AI (Gemini), and a multi-service architecture. The system acts as Sofia, a professional virtual receptionist for a German dental practice, handling appointment booking, patient inquiries, and practice information entirely in German.

## Architecture Overview

### Core Services Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  LiveKit Server │◄────│   Sofia Agent    │────►│ Dental Calendar │
│   (Voice/RTC)   │     │ (Python/Gemini)  │     │  (Node.js/DB)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                           │
                               │                           │
                        ┌──────▼──────┐           ┌───────▼────────┐
                        │  Sofia Web  │           │  CRM Dashboard │
                        │  Interface  │           │   (Flask/Web)  │
                        └─────────────┘           └────────────────┘
```

### Key Components

- **agent.py**: Main LiveKit voice agent with comprehensive dental practice tools
- **dental-calendar/**: Node.js appointment calendar with real-time updates and voice integration
- **crm/**: Flask-based CRM dashboard for practice staff
- **sofia_websocket_bridge.py**: WebSocket bridge for browser-agent communication
- **k8s/**: Kubernetes deployment configurations

## Development Commands

### Quick Start Development

```bash
# Full system with voice (Windows)
start_sofia_calendar.bat

# Individual services
python agent.py dev              # Sofia voice agent
cd dental-calendar && npm start  # Calendar UI
cd crm && python app.py         # CRM dashboard
python sofia_web.py              # Web interface
```

### Docker Development

```bash
# Start all services with Docker Compose
docker-compose up

# Individual service development
docker-compose up livekit         # Just LiveKit server
docker-compose up sofia-agent     # Just Sofia agent
docker-compose up dental-calendar # Just calendar
```

### Testing Commands

```bash
# Voice agent testing
python agent.py console           # Console mode (no LiveKit)
python demo_agent.py             # Simple demo mode
python test_german_agent.py      # Test German interactions

# Integration testing
python test_calendar_integration.py  # Calendar integration
python test_terminverwaltung.py     # Appointment management
python test_full_integration.py     # Full system test

# Specific feature tests
python tests/test_deutsche_uebersetzung.py  # German translation
python tests/test_begruessung_wiederherstellung.py  # Greeting tests
python tests/test_intelligente_vorschlaege.py  # Smart suggestions
```

### Deployment Commands

```bash
# PowerShell deployment to Kubernetes
./deploy.ps1                     # Full deployment
./deploy.ps1 -BuildOnly         # Build images only
./deploy.ps1 -DeployOnly        # Deploy without building

# Docker deployment
docker-compose -f docker-compose.yml up -d  # Production mode
docker-compose -f docker-compose.simple.yml up  # Simple mode
```

## Code Structure

### Source Organization

```
src/
├── agent/           # Voice agent logic
│   ├── agent.py    # Agent implementation
│   └── prompts.py  # German persona & instructions
├── dental/         # Dental practice functionality
│   ├── dental_tools.py       # All appointment & patient tools
│   └── appointment_manager.py # SQLite appointment storage
├── database/       # Data management
│   └── patient_database.py   # JSON patient storage
├── knowledge/      # Practice information
│   └── clinic_knowledge.py   # Services, hours, FAQs
└── utils/          # Utilities
    ├── enhanced_calendar_client.py
    └── german_conversation_flows.py
```

### Key Integration Points

1. **Voice-Calendar Integration**: 
   - Sofia agent connects to dental-calendar via HTTP API
   - Real-time appointment updates via WebSocket
   - Calendar UI includes voice button for Sofia interaction

2. **Database Architecture**:
   - SQLite: `termine.db` for appointments
   - JSON: `data/patients.json` for patient info
   - Shared volume in Docker for data persistence

3. **WebSocket Bridge**:
   - Enables browser-to-agent communication
   - Handles LiveKit token generation
   - Manages room connections

## Critical Functions & Tools

### Appointment Management
- `termin_buchen_calendar_system()` - Calendar integration booking
- `sofia_naechster_freier_termin()` - Next available appointment
- `sofia_terminvorschlaege_intelligent()` - Smart appointment suggestions
- `check_verfuegbarkeit_spezifisch()` - Specific availability checking

### Conversation Management
- `get_zeitabhaengige_begruessung()` - Time-aware greetings
- `gespraech_beenden()` - Conversation ending
- `intelligente_antwort_mit_namen_erkennung()` - Name recognition
- `call_manager` - Call state management

### Patient Interaction
- `collect_patient_info()` - Patient data collection
- `get_patientenhistorie()` - Patient history retrieval
- `medizinische_nachfragen_stellen()` - Medical follow-ups

## Environment Configuration

### Required .env Variables
```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-url  # or ws://localhost:7880 for dev
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# Google AI
GOOGLE_API_KEY=your-google-ai-key

# Calendar Integration
CALENDAR_URL=http://localhost:3005  # or http://dental-calendar:3005 in Docker
```

## Development Guidelines

### Language & Localization
- All user-facing text must be in German
- Use formal "Sie" address for patients
- Time format: 24-hour (e.g., "14:30 Uhr")
- Date format: DD.MM.YYYY

### Voice Interaction Patterns
- Always start with time-appropriate greeting
- Automatically end calls when patient says goodbye
- Handle interruptions gracefully
- Provide clear appointment confirmations

### Testing Strategy
1. Unit tests for individual functions
2. Integration tests for service communication
3. Voice interaction tests with German scenarios
4. End-to-end appointment booking flows

### Common Development Tasks

```bash
# Add new appointment function
# 1. Add to src/dental/dental_tools.py
# 2. Import in agent.py tools list
# 3. Test with: python test_terminverwaltung.py

# Update German responses
# 1. Modify src/agent/prompts.py
# 2. Test with: python agent.py console

# Debug voice issues
# 1. Check: python test_audio.py
# 2. Verify LiveKit: docker logs <container>
# 3. Test WebSocket: python test_sofia_calendar_connection.py
```

## Debugging & Monitoring

### Log Locations
- Sofia Agent: Console output or `sofia_websocket_bridge.log`
- Calendar: Console output from Node.js
- LiveKit: Docker container logs

### Common Issues & Solutions
1. **No audio**: Check microphone permissions, LiveKit connection
2. **German not working**: Verify language="de-DE" in agent config
3. **Appointments not saving**: Check termine.db permissions
4. **WebSocket errors**: Ensure all services are running

### Health Checks
- Sofia Agent: http://localhost:8080/health
- Calendar: http://localhost:3005
- CRM: http://localhost:5000

## Production Considerations

### Kubernetes Deployment
- Uses k8s/ directory configurations
- Includes health checks and resource limits
- Supports horizontal scaling
- Ingress for external access

### Security
- API keys in environment variables
- Patient data encrypted at rest
- HTTPS for production deployments
- Role-based access in CRM

### Performance
- LiveKit handles voice processing
- SQLite suitable for small-medium practices
- Consider PostgreSQL for larger deployments
- Redis for session management (future)