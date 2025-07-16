# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is ELO German - a German dental practice AI assistant built with LiveKit and Google AI (Gemini). The system acts as a virtual receptionist for a German dental practice, handling appointments, patient inquiries, and providing practice information entirely in German.

## Key Architecture

### Core Components

- **agent.py**: Main LiveKit agent application with voice interaction
- **src/dental/dental_tools.py**: Comprehensive dental practice functions (appointment booking, patient management, etc.)
- **src/agent/prompts.py**: German AI persona and instructions for Sofia (virtual receptionist)
- **src/knowledge/clinic_knowledge.py**: Practice data, services, opening hours, and FAQ information
- **src/database/patient_database.py**: JSON-based patient data management
- **src/dental/appointment_manager.py**: SQLite-based appointment management
- **crm/**: Web-based CRM dashboard for appointment management

### Data Storage

- **termine.db**: SQLite database for appointments
- **data/patients.json**: Patient information storage
- **data/**: General data directory

## Development Commands

### Running the Application

```bash
# Development mode with LiveKit
python agent.py dev

# Production mode
python agent.py start

# Console test mode (without LiveKit)
python agent.py console

# Demo version (console-only)
python demo_agent.py
```

### CRM Dashboard

```bash
# Navigate to CRM directory
cd crm

# Start web dashboard
python app.py
# or
start_crm.bat
```

### Testing

```bash
# Run individual test files
python test_german_agent.py
python test_terminverwaltung.py
python test_full_integration.py

# Run specific test modules
python tests/test_volltest_final.py
python tests/test_deutsche_uebersetzung.py
```

### Environment Setup

```bash
# Create virtual environment
python -m venv dental_env

# Activate (Windows)
dental_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Required Environment Variables

Create a `.env` file with:
```
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
GOOGLE_API_KEY=your-google-ai-key
```

## Code Architecture Details

### Agent System (agent.py)
- Uses LiveKit Agents framework for real-time voice interaction
- Integrates Google AI (Gemini) for natural language processing
- Imports comprehensive dental tools and German prompts
- Handles voice input/output with German TTS

### Dental Tools (src/dental/dental_tools.py)
- **Appointment Management**: `schedule_appointment()`, `cancel_appointment()`, `reschedule_appointment()`
- **Availability Checking**: `check_availability()`, `get_naechste_freie_termine()`
- **Patient Management**: `collect_patient_info()`, `get_patientenhistorie()`
- **Practice Information**: `get_clinic_info()`, `get_services_info()`, `answer_faq()`
- **Time Management**: `get_aktuelle_datetime_info()`, `get_zeitabhaengige_begruessung()`
- **Conversation Control**: `gespraech_beenden()`, `intelligente_antwort_mit_namen_erkennung()`

### German Persona (src/agent/prompts.py)
- Defines Sofia as professional German dental receptionist
- Handles time-aware greetings and responses
- Manages conversation flow and automatic call ending
- Integrates with practice hours and scheduling logic

### Practice Data (src/knowledge/clinic_knowledge.py)
- Contains practice information (Dr. Schmidt's practice)
- Defines services, prices, and treatment descriptions
- Includes German insurance information
- FAQ system for common patient questions

## Key Features

- **Voice-First**: Real-time German voice interaction via LiveKit
- **Time-Aware**: Automatic time/date recognition and context-aware responses
- **Appointment Management**: Full booking, cancellation, and rescheduling
- **Patient Database**: JSON-based patient information storage
- **CRM Integration**: Web dashboard for appointment overview
- **German Language**: Complete German localization for dental practice use

## Development Notes

- The system uses SQLite for appointment storage and JSON for patient data
- All user interactions are in German with professional dental practice terminology
- The agent automatically handles conversation ending when patients say goodbye
- Time-dependent greetings and responses are generated dynamically
- Tests focus on German language interaction and appointment booking flows

## Claude Development Rules

When working on this codebase, follow these 7 rules:

1. **First think through the problem** - Read the codebase for relevant files and write a plan to tasks/todo.md
2. **Create checkable todos** - The plan should have a list of todo items that you can check off as you complete them
3. **Verify before starting** - Before you begin working, check in with the user to verify the plan
4. **Track progress** - Begin working on the todo items, marking them as complete as you go
5. **Provide high-level updates** - Every step of the way, give a high level explanation of what changes you made
6. **Keep it simple** - Make every task and code change as simple as possible. Avoid massive or complex changes. Every change should impact as little code as possible
7. **Add review section** - Finally, add a review section to the todo.md file with a summary of the changes made and any other relevant information