# Sofia Audio Problem - Lösung

## Problem
Sofia verbindet sich, aber es gibt kein Audio, weil:
1. Der Agent wartet auf Job-Requests statt direkt dem Raum beizutreten
2. Der Calendar erstellt keinen Job, sondern verbindet sich direkt

## Lösung

### Option 1: Agent im Connect-Mode starten (Empfohlen)

1. **Stoppe den aktuellen Agent** (Ctrl+C im Agent-Fenster)

2. **Starte den Agent im Connect-Mode:**
   ```
   cd elo-deu
   python agent.py connect
   ```

3. **Der Agent wird automatisch allen Räumen beitreten**

### Option 2: Worker-Mode mit Job Request

1. Behalte den Agent im aktuellen Modus
2. Sende einen Job Request über das LiveKit Dashboard oder API

### Option 3: Modifizierter Agent (Bereits erstellt)

Verwende den speziellen Calendar-Agent:
```
python sofia_calendar_agent.py
```

## Test

1. Agent im Connect-Mode starten
2. Browser neu laden (F5)
3. Sofia Agent Button klicken
4. Im Debug-Fenster sollte jetzt "sofia-agent" oder ähnlich erscheinen
5. Sage "Hallo Sofia"

## Warum passiert das?

LiveKit Agents Framework hat zwei Modi:
- **Worker Mode** (Standard): Wartet auf Job-Anfragen
- **Connect Mode**: Tritt automatisch Räumen bei

Der Calendar erstellt keinen Job, daher muss der Agent im Connect-Mode laufen.