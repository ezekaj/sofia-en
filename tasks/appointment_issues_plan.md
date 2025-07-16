# Plan: 3 Terminverwaltungs-Probleme beheben

## Problem 1: Terminabfrage ohne Identifikation
**Aktuell**: Wenn jemand fragt "Haben Sie Termine frei?", antwortet Sofia direkt mit Terminen
**Gewünscht**: Sofia soll erst nach Name und Telefonnummer fragen, um die richtigen Termine zu finden

### Lösung:
- Bei Fragen nach freien Terminen OHNE persönliche Daten → erst Identifikation
- "Um Ihnen passende Termine vorzuschlagen, benötige ich zunächst Ihren Namen und Ihre Telefonnummer."
- Dann personalisierte Termine basierend auf Patientenhistorie

## Problem 2: Termin-ID wird vorgelesen
**Aktuell**: Sofia liest die technische Termin-ID vor (z.B. "APPT_20240716_1430")
**Gewünscht**: Nur den Grund/Behandlungsart nennen, keine technischen IDs

### Lösung:
- In allen Funktionen die Termin-IDs aus der Ausgabe entfernen
- Stattdessen: "Ihr Termin für [Behandlung] am [Datum] um [Uhrzeit]"
- Funktionen anpassen: `get_tagesplan()`, `meine_termine_finden()`, etc.

## Problem 3: Automatisches Auflegen funktioniert nicht
**Aktuell**: Sofia legt nicht auf, bleibt in der Leitung
**Gewünscht**: Nach Verabschiedung soll Sofia das Gespräch beenden

### Lösung:
- `gespraech_beenden()` Funktion überprüfen
- Sicherstellen dass nach Abschiedsworten die Funktion aufgerufen wird
- Prüfen ob die Funktion korrekt implementiert ist

## Implementierungsschritte

### Schritt 1: Terminabfrage-Flow anpassen
```python
# Wenn "Termine frei?" ohne persönliche Daten:
if "termine frei" in input and not has_patient_data:
    return "Gerne schaue ich nach freien Terminen. Darf ich zunächst Ihren Namen erfahren?"
```

### Schritt 2: ID-Ausgabe entfernen
- Alle Stellen finden wo Termin-IDs ausgegeben werden
- Format ändern zu benutzerfreundlicher Ausgabe
- Besonders in: `get_tagesplan()`, `meine_termine_finden()`, `termin_suchen()`

### Schritt 3: Auflegen-Funktion prüfen
- `gespraech_beenden()` Implementation checken
- Trigger-Wörter in prompts.py verifizieren
- Sicherstellen dass die Funktion tatsächlich das Gespräch beendet

## Zu ändernde Dateien

1. **src/dental/dental_tools.py**
   - Terminabfrage-Logik erweitern
   - ID-Ausgabe in allen relevanten Funktionen entfernen
   - `gespraech_beenden()` überprüfen

2. **src/agent/prompts.py**
   - Anweisungen für Identifikation bei Terminabfragen
   - Verstärkte Betonung auf automatisches Auflegen

## Testfälle

1. **Test 1**: "Haben Sie morgen Termine frei?"
   - Erwartet: "Darf ich zunächst Ihren Namen erfahren?"

2. **Test 2**: Terminanzeige
   - Erwartet: "Termin für Zahnreinigung am 17.07. um 14:00"
   - NICHT: "APPT_20240717_1400"

3. **Test 3**: "Danke, auf Wiedersehen"
   - Erwartet: Sofia beendet das Gespräch automatisch