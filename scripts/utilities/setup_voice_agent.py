#!/usr/bin/env python3
"""
Setup Script für Sofia Voice Agent
Hilft beim Einrichten der benötigten API-Keys und Services
"""
import os
import sys
from dotenv import load_dotenv

def check_requirements():
    """Prüft ob alle Requirements installiert sind"""
    print("🔍 Prüfe Requirements...")
    
    try:
        import livekit
        print("✅ LiveKit installiert")
    except ImportError:
        print("❌ LiveKit nicht installiert")
        return False
    
    try:
        import google.generativeai
        print("✅ Google AI installiert")
    except ImportError:
        print("❌ Google AI nicht installiert")
        return False
    
    return True

def setup_google_ai():
    """Hilft beim Einrichten der Google AI API"""
    print("\n🤖 Google AI Setup")
    print("=" * 50)
    print("1. Gehen Sie zu: https://aistudio.google.com/")
    print("2. Erstellen Sie einen kostenlosen API-Key")
    print("3. Kopieren Sie den API-Key")
    
    api_key = input("\nGeben Sie Ihren Google AI API-Key ein (oder Enter zum Überspringen): ").strip()
    
    if api_key:
        # Update .env file
        update_env_file("GOOGLE_API_KEY", api_key)
        print("✅ Google AI API-Key gespeichert!")
        return True
    else:
        print("⚠️ Google AI API-Key übersprungen")
        return False

def setup_livekit():
    """Hilft beim Einrichten von LiveKit"""
    print("\n🎤 LiveKit Setup")
    print("=" * 50)
    print("Wählen Sie eine Option:")
    print("1. LiveKit Cloud (Empfohlen - kostenlos)")
    print("2. Lokaler LiveKit Server")
    print("3. Überspringen")
    
    choice = input("\nIhre Wahl (1-3): ").strip()
    
    if choice == "1":
        return setup_livekit_cloud()
    elif choice == "2":
        return setup_livekit_local()
    else:
        print("⚠️ LiveKit Setup übersprungen")
        return False

def setup_livekit_cloud():
    """Setup für LiveKit Cloud"""
    print("\n☁️ LiveKit Cloud Setup")
    print("1. Gehen Sie zu: https://cloud.livekit.io/")
    print("2. Erstellen Sie einen kostenlosen Account")
    print("3. Erstellen Sie ein neues Projekt")
    print("4. Kopieren Sie die Credentials")
    
    url = input("\nLiveKit URL (z.B. wss://your-project.livekit.cloud): ").strip()
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    
    if url and api_key and api_secret:
        update_env_file("LIVEKIT_URL", url)
        update_env_file("LIVEKIT_API_KEY", api_key)
        update_env_file("LIVEKIT_API_SECRET", api_secret)
        print("✅ LiveKit Cloud Credentials gespeichert!")
        return True
    else:
        print("❌ Unvollständige LiveKit Credentials")
        return False

def setup_livekit_local():
    """Setup für lokalen LiveKit Server"""
    print("\n🏠 Lokaler LiveKit Server")
    print("Für lokale Entwicklung können wir einen einfachen Setup verwenden:")
    
    # Set default local credentials
    update_env_file("LIVEKIT_URL", "ws://localhost:7880")
    update_env_file("LIVEKIT_API_KEY", "devkey")
    update_env_file("LIVEKIT_API_SECRET", "secret")
    
    print("✅ Lokale LiveKit Credentials gesetzt!")
    print("💡 Sie müssen noch einen LiveKit Server starten:")
    print("   - Download: https://github.com/livekit/livekit/releases")
    print("   - Oder: livekit-server --dev")
    
    return True

def update_env_file(key, value):
    """Aktualisiert die .env Datei"""
    env_path = ".env"
    
    # Read current content
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    
    # Update or add the key
    key_found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_found = True
            break
    
    if not key_found:
        lines.append(f"{key}={value}\n")
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)

def test_setup():
    """Testet die Konfiguration"""
    print("\n🧪 Teste Konfiguration...")
    
    load_dotenv()
    
    # Test Google AI
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key and google_key != "your-google-ai-key":
        print("✅ Google AI API-Key konfiguriert")
    else:
        print("❌ Google AI API-Key fehlt")
    
    # Test LiveKit
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_key = os.getenv("LIVEKIT_API_KEY")
    livekit_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if (livekit_url and livekit_url != "wss://your-livekit-url" and
        livekit_key and livekit_key != "your-api-key" and
        livekit_secret and livekit_secret != "your-api-secret"):
        print("✅ LiveKit Credentials konfiguriert")
        return True
    else:
        print("❌ LiveKit Credentials fehlen")
        return False

def main():
    """Hauptfunktion"""
    print("🚀 Sofia Voice Agent Setup")
    print("=" * 50)
    
    if not check_requirements():
        print("\n❌ Bitte installieren Sie zuerst alle Requirements:")
        print("pip install -r requirements.txt")
        return
    
    # Setup APIs
    google_ok = setup_google_ai()
    livekit_ok = setup_livekit()
    
    # Test configuration
    if test_setup():
        print("\n🎉 Setup erfolgreich!")
        print("\nSo starten Sie Sofia:")
        print("python agent.py dev")
        print("\nOder für Konsolen-Demo:")
        print("python demo_agent.py")
    else:
        print("\n⚠️ Setup unvollständig. Bitte konfigurieren Sie die fehlenden APIs.")

if __name__ == "__main__":
    main()
