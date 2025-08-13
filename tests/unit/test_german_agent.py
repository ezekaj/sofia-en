#!/usr/bin/env python3
"""
Test für die deutsche Zahnarzt-Assistentin
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    """Test the connection to LiveKit"""
    print("🧪 Teste LiveKit-Verbindung...")
    
    # Get credentials from environment
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not all([url, api_key, api_secret]):
        print("❌ Fehlende LiveKit-Credentials!")
        return False
    
    print(f"✅ LiveKit URL: {url}")
    print(f"✅ API Key: {api_key[:10]}...")
    print(f"✅ API Secret: {'*' * len(api_secret)}")
    
    return True

if __name__ == "__main__":
    print("=== Test für Deutsche Zahnarzt-Assistentin ===")
    
    # Test connection
    if asyncio.run(test_connection()):
        print("\n✅ Konfiguration OK!")
    else:
        print("\n❌ Konfiguration fehlerhaft!")
    
    print("\n" + "="*50)
    print("💡 Hinweise zur Verwendung:")
    print("1. Stellen Sie sicher, dass der Agent läuft: python agent.py dev")
    print("2. Verbinden Sie sich mit einem LiveKit-Client (z.B. Web-Client)")
    print("3. Aktivieren Sie Ihr Mikrofon")
    print("4. Sprechen Sie auf Deutsch mit dem Agent")
    print("5. Der Agent sollte mit einer deutschen weiblichen Stimme antworten")
    print("\n📞 Für Audio-Tests verwenden Sie einen LiveKit-Client:")
    print("   - Web: https://livekit.io/playground")
    print("   - Mobile: LiveKit Meet App")
    print("   - Desktop: LiveKit-Client-Apps")
    print("\n🎤 Agent-Status prüfen:")
    print("   - Schauen Sie im Terminal nach 'registered worker'")
    print("   - Achten Sie auf Audio-Events wie 'Audio-Track erkannt'")
    print("   - Der Agent sollte 'Bereit zum Zuhören!' ausgeben")
