#!/usr/bin/env python3
"""
Sofia WebSocket Bridge Startup Script
=====================================

This script starts the Sofia WebSocket Bridge server with proper configuration
and environment setup. It handles all necessary initialization and provides
a clean startup process.

Usage:
    python start_sofia_websocket_bridge.py [--dev] [--port 8765] [--host localhost]

Author: Sofia WebSocket Bridge System
Version: 1.0.0
"""

import os
import sys
import argparse
import logging
import asyncio
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_environment():
    """Setup environment variables and configuration"""
    
    # Set default environment variables if not present
    env_defaults = {
        'OPENAI_API_KEY': '',  # User must provide this
        'GOOGLE_APPLICATION_CREDENTIALS': '',  # User must provide this
        'LIVEKIT_URL': 'ws://localhost:7880',
        'LIVEKIT_API_KEY': 'devkey',
        'LIVEKIT_API_SECRET': 'secret',
        'CALENDAR_URL': 'http://localhost:3005',
        'LOG_LEVEL': 'INFO',
        'PYTHON_ENV': 'development'
    }
    
    for key, default_value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = default_value
    
    # Load .env file if it exists
    env_file = current_dir / '.env'
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)

def check_dependencies():
    """Check if all required dependencies are available"""
    
    required_modules = [
        'websockets',
        'openai',
        'google.cloud.texttospeech',
        'speech_recognition',
        'pydub',
        'aiohttp'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module.replace('.', '/').split('/')[0])
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Missing required dependencies:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\nInstall missing dependencies:")
        print("   pip install -r requirements_websocket_bridge.txt")
        return False
    
    return True

def check_sofia_agent():
    """Check if Sofia agent components are available"""
    
    try:
        # Check if Sofia agent tools are available
        from src.dental.dental_tools import get_clinic_info
        from src.agent.prompts import AGENT_INSTRUCTION
        print("✅ Sofia agent components found")
        return True
    except ImportError as e:
        print(f"❌ Sofia agent components not found: {e}")
        print("Make sure you're running from the correct directory with Sofia agent installed")
        return False

def print_startup_banner():
    """Print startup banner"""
    
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              🦷 Sofia WebSocket Bridge Server 🎤              ║
    ║                                                              ║
    ║              Fallback Voice Interface for Sofia             ║
    ║                     Version 1.0.0                           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_configuration(args):
    """Print current configuration"""
    
    print("🔧 Configuration:")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Health Port: {args.health_port}")
    print(f"   Debug Mode: {args.debug}")
    print(f"   Development Mode: {args.dev}")
    print()
    
    print("🌍 Environment:")
    print(f"   OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print(f"   Google TTS Credentials: {'✅ Set' if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') else '❌ Not set'}")
    print(f"   Calendar URL: {os.getenv('CALENDAR_URL', 'Not set')}")
    print(f"   LiveKit URL: {os.getenv('LIVEKIT_URL', 'Not set')}")
    print(f"   Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
    print()

def print_usage_instructions(args):
    """Print usage instructions"""
    
    print("📋 Usage Instructions:")
    print(f"   • WebSocket URL: ws://{args.host}:{args.port}")
    print(f"   • Health Check: http://{args.host}:{args.health_port}/health")
    print(f"   • Test Interface: http://localhost:3005/sofia-websocket-test.html")
    print()
    
    print("🎤 Audio Features:")
    if os.getenv('OPENAI_API_KEY'):
        print("   • OpenAI Whisper transcription: ✅ Enabled")
    else:
        print("   • OpenAI Whisper transcription: ❌ Disabled (fallback available)")
    
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("   • Google Text-to-Speech: ✅ Enabled")
    else:
        print("   • Google Text-to-Speech: ❌ Disabled")
    print()
    
    print("🗓️ Sofia Features:")
    print("   • German conversation handling: ✅ Enabled")
    print("   • Appointment booking: ✅ Enabled")
    print("   • Calendar integration: ✅ Enabled")
    print("   • Multi-session support: ✅ Enabled")
    print()
    
    print("⌨️ Controls:")
    print("   • Ctrl+C: Stop server")
    print("   • Space key (browser): Push-to-talk")
    print("   • Enter key (browser): Send text message")
    print()

async def start_bridge_server(args):
    """Start the WebSocket bridge server"""
    
    try:
        # Import bridge components
        from sofia_websocket_bridge import SofiaWebSocketBridge, HealthCheckServer
        
        # Create bridge instance
        bridge = SofiaWebSocketBridge(host=args.host, port=args.port)
        
        # Create health check server
        health_server = HealthCheckServer(bridge, port=args.health_port)
        
        # Start health check server
        print("🏥 Starting health check server...")
        await health_server.start()
        
        # Start main bridge server
        print("🚀 Starting Sofia WebSocket Bridge...")
        await bridge.start_server()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Sofia WebSocket Bridge...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def main():
    """Main entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Sofia WebSocket Bridge Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_sofia_websocket_bridge.py
  python start_sofia_websocket_bridge.py --dev --debug
  python start_sofia_websocket_bridge.py --host 0.0.0.0 --port 9000
        """
    )
    
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8765, help='Port to bind to (default: 8765)')
    parser.add_argument('--health-port', type=int, default=8766, help='Health check port (default: 8766)')
    parser.add_argument('--dev', action='store_true', help='Enable development mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Print startup banner
    print_startup_banner()
    
    # Setup environment
    print("🔧 Setting up environment...")
    setup_environment()
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        return 1
    
    # Check Sofia agent
    print("🤖 Checking Sofia agent...")
    if not check_sofia_agent():
        return 1
    
    # Setup logging
    log_level = logging.DEBUG if args.debug or args.dev else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('sofia_websocket_bridge.log'),
            logging.StreamHandler()
        ]
    )
    
    # Print configuration
    print_configuration(args)
    
    # Print usage instructions
    print_usage_instructions(args)
    
    # Start the server
    try:
        return asyncio.run(start_bridge_server(args))
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0

if __name__ == "__main__":
    sys.exit(main())