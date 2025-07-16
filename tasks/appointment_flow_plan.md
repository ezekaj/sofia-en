# Plan: Terminanfrage-Flow verbessern

## Problem
Wenn ein Patient nur sagt "Ich möchte einen Termin", fragt Sofia derzeit nach der Zeit, bevor sie nach dem Grund/Behandlungsart fragt. Das ist nicht optimal.

## Gewünschter Flow
1. Patient: "Ich möchte einen Termin"
2. Sofia: "Gerne! Wofür benötigen Sie denn den Termin?" (GRUND ZUERST)
3. Patient: "Zahnreinigung" / "Ich habe Schmerzen" / etc.
4. Sofia: "Alles klar, eine Zahnreinigung. Wann hätten Sie denn Zeit?"

## Zu ändernde Dateien

### 1. src/agent/prompts.py
- [ ] Beispiel-Dialog anpassen (Zeilen 168-177)
- [ ] Workflow-Anweisungen aktualisieren (Zeilen 150-154)
- [ ] Neues Beispiel für korrekten Flow hinzufügen

### 2. src/dental/dental_tools.py
- [ ] `intelligente_antwort_mit_namen_erkennung()` (Zeile 1824)
  - Statt "Wann hätten Sie Zeit?" → "Wofür benötigen Sie denn den Termin?"
- [ ] Neue Hilfsfunktion für Behandlungsart-Erkennung
- [ ] Integration mit Lernfähigkeit für häufige Behandlungsgründe

## Implementierungsschritte

### Schritt 1: Prompts anpassen
```python
# Alter Flow:
**Patient**: "Ich möchte einen Termin"
**Sofia**: "Gerne! Wann hätten Sie Zeit?"

# Neuer Flow:
**Patient**: "Ich möchte einen Termin"
**Sofia**: "Gerne vereinbare ich einen Termin für Sie. Wofür benötigen Sie denn den Termin?"
**Patient**: "Zahnreinigung"
**Sofia**: "Perfekt, eine Zahnreinigung dauert etwa 45 Minuten. Wann hätten Sie denn Zeit?"
```

### Schritt 2: Funktion anpassen
Die Funktion soll:
1. Erkennen wenn nur "Termin" ohne Grund erwähnt wird
2. Nach dem Grund fragen
3. Basierend auf dem Grund passende Zeitslots vorschlagen
4. Dann erst nach der bevorzugten Zeit fragen

### Schritt 3: Lernfähigkeit nutzen
- Häufige Gründe tracken
- Bei bekannten Patienten eventuell vorschlagen: "Ist es wieder Zeit für Ihre Zahnreinigung?"

## Vorteile
1. **Bessere Priorisierung**: Schmerzpatienten können schneller eingeplant werden
2. **Passende Zeitslots**: Basierend auf Behandlungsdauer
3. **Professioneller Flow**: Entspricht echtem Praxisablauf
4. **Lerneffekt**: System merkt sich häufige Behandlungsgründe

## Testing
- Verschiedene Terminanfragen ohne Grund testen
- Sicherstellen dass der Flow natürlich wirkt
- Überprüfen dass alle Informationen korrekt gesammelt werden