# CLAUDE.md

This file provides guidance when working with code in this repository.

## Project Overview

Sofia Base Agent - A foundational AI voice assistant built with LiveKit and Google AI (Gemini). This is the base, generic version of Sofia that serves as a starting point for specialized implementations. Sofia Base provides core voice interaction capabilities without any specific industry or use-case specialization.

## Architecture Overview

### Core Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  LiveKit Server │◄────│  Sofia Base      │────►│  Generic Tools  │
│   (Voice/RTC)   │     │  (Python/Gemini) │     │  & Functions    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               │
                        ┌──────▼──────┐
                        │  Base Tools │
                        │  & Prompts  │
                        └─────────────┘
```

### Key Components

- **agent.py**: Main Sofia base voice agent with core functionality
- **src/agent/prompts.py**: Generic Sofia personality and instructions
- **src/agent/tools.py**: Basic tools for time, greetings, and general help
- **Base Architecture**: Foundation for specialized Sofia implementations

## Development Commands

### Quick Start Development

```bash
# Sofia Base Agent
python agent.py                # Sofia base voice agent
python agent.py console        # Console mode indication

# Testing
python -c "from src.agent.tools import *; print('Tools imported successfully')"
```

### Testing Commands

```bash
# Basic functionality test
python agent.py console         # Test agent initialization

# Tools testing
python -c "
import asyncio
from src.agent.tools import get_time_based_greeting, get_current_datetime_info
async def test():
    print(await get_time_based_greeting(None))
    print(await get_current_datetime_info(None))
asyncio.run(test())
"
```

## Code Structure

### Source Organization

```
src/
├── agent/          # Core agent logic
│   ├── prompts.py  # Sofia base personality & instructions
│   ├── tools.py    # Generic tools (time, greeting, help)
│   └── __init__.py
└── __init__.py
```

### Key Files

- **agent.py**: Main entry point for Sofia Base Agent
- **src/agent/prompts.py**: Core personality and conversation instructions
- **src/agent/tools.py**: Basic tools that any Sofia variant can use

## Core Functionality

### Base Tools Available

1. **Time & Greeting Management**:
   - `get_current_datetime_info()` - Comprehensive time/date information
   - `get_time_based_greeting()` - Appropriate greetings based on time

2. **General Assistance**:
   - `get_basic_info()` - Sofia's basic capabilities information
   - `general_help()` - Help and usage guidance

3. **Conversation Management**:
   - `end_conversation()` - Polite conversation ending

### Sofia Base Personality

- **Generic AI Assistant**: Not specialized for any particular industry
- **Professional & Helpful**: Maintains professional demeanor while being friendly
- **Time Aware**: Provides appropriate greetings based on current time
- **Adaptable**: Designed to be extended for specific use cases

## Environment Configuration

### Required .env Variables
```bash
# LiveKit Configuration
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# Google AI
GOOGLE_API_KEY=your_google_api_key_here

# Optional Database (for specializations)
DATABASE_URL=sqlite:///sofia.db
```

## Development Guidelines

### Creating Specialized Sofia Variants

1. **Fork this base repository** for your specialized implementation
2. **Keep base tools**: Use existing time/greeting/help functions
3. **Add specialized tools**: Create domain-specific functions
4. **Update prompts**: Modify personality for your use case
5. **Extend capabilities**: Add industry-specific knowledge and functions

### Language & Communication
- **Language**: English (US) by default
- **Tone**: Professional yet warm and approachable
- **Clarity**: Clear, concise communication
- **Adaptability**: Generic responses that work in any context

### Code Standards
- **Modular Design**: Keep tools and prompts separate and extensible
- **Clear Documentation**: Document all functions and capabilities
- **Error Handling**: Graceful handling of errors and edge cases
- **Testing**: Ensure all base functionality works before specialization

## Extending Sofia Base

### For Specific Industries

```bash
# Example: Creating Sofia Hotel Concierge
1. Fork sofia-base repository
2. Add hotel-specific tools: book_room(), check_availability()
3. Update prompts: Add hotel persona and knowledge
4. Add industry data: Hotel information, services, pricing
5. Test specialized functionality
```

### For Different Use Cases

```bash
# Example: Creating Sofia Medical Assistant
1. Clone base architecture
2. Add medical tools: schedule_appointment(), get_symptoms()
3. Update personality: Add medical expertise and compliance
4. Add knowledge base: Medical information and protocols
5. Implement specialized workflows
```

## Common Development Tasks

```bash
# Test base functionality
python agent.py console

# Verify tools import correctly
python -c "from src.agent.tools import *; print('All tools available')"

# Check prompts
python -c "from src.agent.prompts import *; print('Prompts loaded')"

# Basic conversation flow test
python agent.py  # Start and test with LiveKit
```

## Production Deployment

### Base Agent Deployment
- **Containerization**: Uses Docker for consistent deployment
- **Environment**: Configure .env for production settings
- **Scaling**: LiveKit handles voice processing and scaling
- **Monitoring**: Basic health checks and logging included

### Security Considerations
- **API Keys**: Store in environment variables, not code
- **Generic Response**: No sensitive industry-specific information in base
- **Extensible Security**: Add security measures when specializing

## Base Agent Capabilities

### What Sofia Base CAN Do
- ✅ Provide time-appropriate greetings
- ✅ Handle basic conversation flow
- ✅ Give general assistance and information
- ✅ Manage conversation endings gracefully
- ✅ Maintain professional, helpful persona
- ✅ Serve as foundation for specialization

### What Sofia Base CANNOT Do (By Design)
- ❌ Industry-specific tasks (medical, hotel, legal, etc.)
- ❌ Complex business logic or workflows
- ❌ Database operations beyond basic configuration
- ❌ Specialized knowledge or expertise
- ❌ Domain-specific tool functions

## Next Steps

To create a specialized Sofia agent:

1. **Use this as your foundation**: Clone or fork sofia-base
2. **Add your domain expertise**: Create specialized tools and knowledge
3. **Customize personality**: Update prompts for your use case
4. **Test thoroughly**: Ensure base + specialized functionality works
5. **Deploy confidently**: Use proven base architecture

Sofia Base provides the reliable foundation - you add the specialization!