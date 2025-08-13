# Sofia WebSocket Bridge

A comprehensive WebSocket-based fallback solution for the Sofia voice agent browser integration. This system provides a robust alternative to LiveKit that allows browser users to interact with Sofia through WebSockets while maintaining full compatibility with the existing Sofia agent.

## 🎯 Overview

The Sofia WebSocket Bridge acts as an intermediary layer between web browsers and the Sofia dental assistant agent. It provides voice interaction, text chat, and appointment booking capabilities without requiring LiveKit infrastructure.

### Key Features

- 🎤 **Voice Interaction**: Real-time audio recording, transcription, and text-to-speech
- 💬 **Text Chat**: Traditional text-based conversation interface
- 🗓️ **Appointment Management**: Integration with existing calendar system
- 👥 **Multi-Session Support**: Handle multiple concurrent browser sessions
- 🔄 **Auto-Reconnection**: Robust connection handling with automatic recovery
- 🛡️ **Error Handling**: Comprehensive error handling and fallback mechanisms
- 📊 **Performance Monitoring**: Built-in statistics and health monitoring
- 🌐 **Browser Compatibility**: Works with all modern web browsers

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket     ┌──────────────────┐    Sofia Tools    ┌─────────────────┐
│                 │ ◄─────────────► │                  │ ◄───────────────► │                 │
│  Browser Client │                 │  WebSocket Bridge │                   │  Sofia Agent    │
│                 │                 │                  │                   │                 │
└─────────────────┘                 └──────────────────┘                   └─────────────────┘
                                            │
                                            ▼
                                    ┌──────────────────┐
                                    │                  │
                                    │ Sofia Adapter    │
                                    │                  │
                                    └──────────────────┘
                                            │
                                            ▼
                                    ┌──────────────────┐
                                    │                  │
                                    │ Calendar System  │
                                    │                  │
                                    └──────────────────┘
```

## 📦 Components

### 1. WebSocket Bridge Server (`sofia_websocket_bridge.py`)
- Main WebSocket server handling client connections
- Audio processing with OpenAI Whisper and Google TTS
- Session management and statistics
- Health monitoring and cleanup

### 2. Sofia Agent Adapter (`sofia_agent_adapter.py`)
- Translation layer between WebSocket bridge and Sofia agent
- Intent classification and conversation management
- Direct integration with Sofia's dental tools
- German language processing

### 3. Browser Client (`sofia-websocket-client.js`)
- JavaScript client for browser integration
- Audio recording and playback
- Real-time WebSocket communication
- Session persistence and reconnection

### 4. Test Interface (`sofia-websocket-test.html`)
- Comprehensive testing interface
- Voice and text interaction
- Quick appointment booking
- Debug tools and statistics

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for calendar system)
- Modern web browser with microphone support

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements_websocket_bridge.txt
```

2. **Set up environment variables:**
```bash
# Optional: OpenAI API key for better transcription
export OPENAI_API_KEY="your_openai_api_key"

# Optional: Google Cloud credentials for text-to-speech
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"

# Calendar system URL
export CALENDAR_URL="http://localhost:3005"
```

3. **Start the calendar system:**
```bash
cd dental-calendar
npm install
npm start
```

4. **Start the WebSocket bridge:**
```bash
# Windows
start_sofia_websocket_bridge.bat

# Linux/Mac
python start_sofia_websocket_bridge.py --dev
```

5. **Open test interface:**
   - Navigate to: `http://localhost:3005/sofia-websocket-test.html`
   - Click "Verbinden" to connect
   - Start chatting with Sofia!

## 🎤 Audio Configuration

### OpenAI Whisper (Recommended)
```bash
export OPENAI_API_KEY="your_api_key_here"
```
- Provides high-quality German transcription
- Supports multiple audio formats
- Automatic language detection

### Google Text-to-Speech (Optional)
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```
- Generates natural German speech
- Multiple voice options available
- High-quality audio output

### Fallback Options
- **Transcription**: Uses SpeechRecognition library with Google Speech API
- **Text-to-Speech**: Disabled (text-only responses)

## 💻 Usage

### Browser Interface

1. **Connect to Sofia:**
   - Enter your name and phone number
   - Click "Verbinden" to establish connection
   - Wait for confirmation message

2. **Voice Interaction:**
   - Hold microphone button to speak
   - Or use spacebar for push-to-talk
   - Release to send audio to Sofia

3. **Text Chat:**
   - Type message in text field
   - Press Enter or click "Senden"
   - Receive both text and audio responses

4. **Quick Appointment Booking:**
   - Fill in date, time, and treatment type
   - Click "Termin buchen"
   - Receive confirmation or alternatives

### Programming Interface

```javascript
// Initialize client
const client = new SofiaWebSocketClient({
    websocketUrl: 'ws://localhost:8765',
    debug: true
});

// Connect and set up events
await client.initialize('container-id');
client.on('connected', () => console.log('Connected!'));
client.on('message', (data) => console.log('Received:', data));

// Connect
await client.connect();

// Send message
client.sendMessage({
    type: 'text_message',
    message: 'Hallo Sofia, ich möchte einen Termin buchen'
});
```

## 🔧 Configuration

### WebSocket Bridge Settings

```python
# Host and port configuration
host = "localhost"  # Use "0.0.0.0" for external access
port = 8765         # WebSocket port
health_port = 8766  # Health check port

# Audio settings
audio_sample_rate = 16000
audio_buffer_size = 4096

# Session settings
session_timeout = 1800  # 30 minutes
cleanup_interval = 300  # 5 minutes
```

### Browser Client Settings

```javascript
const client = new SofiaWebSocketClient({
    websocketUrl: 'ws://localhost:8765',
    reconnectInterval: 3000,
    maxReconnectAttempts: 10,
    audioSampleRate: 16000,
    autoReconnect: true,
    debug: false
});
```

## 📊 Monitoring

### Health Check Endpoint
- URL: `http://localhost:8766/health`
- Returns: Server status, statistics, and uptime

### Debug Interface
- Real-time connection status
- Message statistics
- Audio processing metrics
- Session information

### Logging
- File: `sofia_websocket_bridge.log`
- Levels: DEBUG, INFO, WARNING, ERROR
- Structured logging with timestamps

## 🛠️ Development

### Running in Development Mode
```bash
python start_sofia_websocket_bridge.py --dev --debug
```

### Testing
```bash
# Unit tests (if implemented)
pytest tests/

# Manual testing
# 1. Open sofia-websocket-test.html
# 2. Connect to bridge
# 3. Test voice and text interaction
# 4. Verify appointment booking
```

### Debug Console Functions
```javascript
// Browser console debug functions
debug.getClient()     // Get client instance
debug.getStats()      // View connection statistics
debug.connect()       // Connect to server
debug.disconnect()    // Disconnect from server
debug.sendMessage("Hello Sofia")  // Send test message
```

## 🔒 Security Considerations

### Network Security
- Use HTTPS/WSS in production
- Implement proper CORS policies
- Consider rate limiting for API endpoints

### Data Privacy
- Audio data is processed in real-time (not stored)
- Session data is temporary and cleaned up
- No persistent audio recording

### Authentication
- Basic session-based identification
- No built-in user authentication (add as needed)
- Phone number validation for appointments

## 🚨 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check if bridge server is running
   - Verify WebSocket URL and port
   - Check firewall settings

2. **Audio Not Working**
   - Grant microphone permissions
   - Check browser compatibility
   - Verify audio service configuration

3. **Transcription Errors**
   - Check OpenAI API key
   - Verify internet connection
   - Try fallback transcription method

4. **TTS Not Working**
   - Check Google Cloud credentials
   - Verify TTS service setup
   - Text responses will still work

5. **Appointment Booking Failed**
   - Check calendar system connection
   - Verify user information is complete
   - Check appointment availability

### Debug Steps

1. **Check Server Logs:**
```bash
tail -f sofia_websocket_bridge.log
```

2. **Verify Services:**
```bash
# Check WebSocket bridge
curl http://localhost:8766/health

# Check calendar system
curl http://localhost:3005/health
```

3. **Browser Console:**
```javascript
// Check client status
debug.getClient().connectionState

// View detailed statistics
debug.getStats()
```

## 📈 Performance Optimization

### Audio Processing
- Use WebM/Opus for better compression
- Implement audio buffer management
- Consider client-side noise reduction

### WebSocket Optimization
- Enable compression for text messages
- Implement message queuing
- Use connection pooling for high load

### Memory Management
- Regular session cleanup
- Audio buffer limits
- Connection timeout handling

## 🔄 Updates and Maintenance

### Regular Maintenance
- Monitor log files for errors
- Clean up old session data
- Update dependencies regularly

### Scaling Considerations
- Use Redis for session storage
- Implement load balancing
- Consider containerization with Docker

## 📚 API Reference

### WebSocket Message Types

#### Client to Server:
- `text_message`: Send text to Sofia
- `audio_data`: Send audio recording
- `audio_stream_start/end`: Audio streaming control
- `user_info`: Update user information
- `appointment_request`: Direct appointment booking
- `ping`: Connection keepalive

#### Server to Client:
- `welcome`: Initial connection message
- `text_response`: Sofia's text response
- `audio_response`: Sofia's audio response
- `appointment_confirmed/error`: Booking results
- `error`: Error notifications
- `pong`: Ping response

### Sofia Agent Integration

The bridge integrates with all Sofia agent tools:
- Appointment booking and management
- Clinic information queries
- German conversation handling
- Calendar system integration
- Patient information management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the Sofia dental assistant system. Please refer to the main project license.

## 📞 Support

For technical support or questions:
- Check the troubleshooting section
- Review server logs
- Test with the provided test interface
- Verify all prerequisites are met

---

**Sofia WebSocket Bridge v1.0.0** - A robust fallback solution for Sofia voice agent browser integration.