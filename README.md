# ELO German - Deutsche Zahnarzt-Assistentin

Ein intelligenter deutscher Zahnarzt-Assistent basierend auf LiveKit und Google AI (Gemini), der als Rezeptionistin für eine deutsche Zahnarztpraxis fungiert.

## Features

🎤 **Sprachsteuerung**: Vollständige deutsche Sprachunterstützung mit weiblicher Stimme
🏥 **Zahnarztpraxis-Funktionen**: Termine buchen, Praxisinfos, Behandlungsberatung
🤖 **KI-Powered**: Verwendet Google Gemini für natürliche Konversationen
🔊 **LiveKit Integration**: Echzeit-Audio für natürliche Gespräche
📅 **Terminverwaltung**: Intelligente Terminbuchung und -verwaltung

## Hauptfunktionen

- **Terminbuchung**: Automatische Terminvereinbarung mit Verfügbarkeitsprüfung
- **Praxisinformationen**: Öffnungszeiten, Kontaktdaten, Anfahrt
- **Behandlungsberatung**: Informationen zu allen Zahnbehandlungen
- **FAQ-System**: Antworten auf häufige Patientenfragen
- **Versicherungsinfo**: Unterstützung für deutsche Krankenversicherungen
- **Notfalltermine**: Schnelle Hilfe bei Zahnnotfällen

## Installation

1. **Repository klonen**:
```bash
git clone https://github.com/yourusername/elo-german.git
cd elo-german
```

2. **Virtual Environment erstellen**:
```bash
python -m venv dental_env
dental_env\Scripts\activate  # Windows
```

3. **Dependencies installieren**:
```bash
pip install -r requirements.txt
```

4. **Umgebungsvariablen konfigurieren**:
Erstellen Sie eine `.env` Datei mit:
```
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
GOOGLE_API_KEY=your-google-ai-key
```

## Verwendung

### Development-Modus
```bash
python agent.py dev
```

### Produktions-Modus
```bash
python agent.py start
```

### Konsolen-Test
```bash
python agent.py console
```

## Konfiguration

### Praxisinformationen
Die Praxisdaten können in `clinic_knowledge.py` angepasst werden:

- **Praxisname**: Zahnarztpraxis Dr. Schmidt
- **Adresse**: Hauptstraße 123, 10115 Berlin
- **Öffnungszeiten**: Mo-Fr 8:00-18:00, Sa 9:00-13:00
- **Telefon**: +49 30 12345678

### Verfügbare Behandlungen
- Allgemeine Zahnheilkunde
- Professionelle Zahnreinigung
- Kieferorthopädie
- Implantologie
- Ästhetische Zahnheilkunde
- Endodontie
- Oralchirurgie
- Zahnprothetik

### Krankenversicherungen
Unterstützt alle deutschen Krankenkassen:
- AOK, Techniker Krankenkasse, Barmer, DAK, IKK
- Private Versicherungen: Allianz, DKV, Signal Iduna

## Technische Details

### Technologie-Stack
- **LiveKit**: Echzeit-Audio-/Video-Kommunikation
- **Google AI (Gemini)**: Natürliche Sprachverarbeitung
- **Python**: Backend-Implementierung
- **WebRTC**: Browser-basierte Audio-Kommunikation

### Sprachkonfiguration
- **Sprache**: Deutsch (de-DE)
- **Stimme**: Weiblich (Aoede)
- **Noise Cancellation**: Aktiv
- **Audio-Qualität**: HD

### Architektur
```
agent.py              # Hauptanwendung
clinic_knowledge.py   # Praxisdaten
dental_tools.py       # Funktionen
prompts.py           # KI-Anweisungen
```

## Entwicklung

### Debugging
```bash
python microphone_test.py  # Mikrofon-Test
python debug_audio.py dev  # Audio-Debugging
```

### Logs
Alle Logs werden in der Konsole angezeigt. Für detaillierte Debugging-Informationen:
```bash
python agent.py dev --log-level DEBUG
```

## Deployment

### LiveKit Cloud
1. Registrieren Sie sich bei LiveKit Cloud
2. Erstellen Sie ein neues Projekt
3. Kopieren Sie die Credentials in die `.env` Datei
4. Starten Sie den Agent: `python agent.py start`

### Lokaler Test
Für lokale Tests ohne LiveKit:
```bash
python demo_agent.py  # Konsolen-Version
```

## Lizenz

MIT License - Siehe LICENSE Datei für Details.

## Support

Bei Fragen oder Problemen:
1. Prüfen Sie die AUDIO_TROUBLESHOOTING.md
2. Öffnen Sie ein Issue auf GitHub
3. Kontaktieren Sie den Entwickler

## Beitragen

Pull Requests sind willkommen! Für größere Änderungen öffnen Sie bitte zuerst ein Issue.

---

**ELO German** - Ihr intelligenter deutscher Zahnarzt-Assistent 🦷🇩🇪
