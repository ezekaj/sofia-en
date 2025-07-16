# Plan: Deutsche Telefonnummern-Validierung

## Problem
Sofia soll nur Termine für Patienten mit deutschen Telefonnummern (Mobil oder Festnetz) buchen.

## Analyse deutsche Telefonnummern

### Deutsche Festnetznummern
- Format: +49 (Vorwahl) Nummer oder 0(Vorwahl) Nummer
- Beispiele:
  - +49 30 12345678 (Berlin)
  - 030 12345678
  - +49 89 12345678 (München)
  - 089 12345678

### Deutsche Mobilnummern
- Beginnen mit: 015x, 016x, 017x (oder +49 15x, +49 16x, +49 17x)
- Beispiele:
  - +49 151 12345678
  - 0151 12345678
  - +49 170 12345678
  - 0170 12345678

## Implementierungsplan

### Schritt 1: Validierungsfunktion erstellen
```python
def ist_deutsche_nummer(telefon: str) -> bool:
    """
    Prüft ob eine Telefonnummer eine gültige deutsche Nummer ist
    """
    # Bereinige Nummer (Leerzeichen, Bindestriche entfernen)
    # Prüfe Präfixe
    # Validiere Länge
```

### Schritt 2: Integration in Terminbuchung
- In `termin_direkt_buchen()` 
- In `termin_hinzufuegen()` (appointment_manager.py)
- Validierung VOR dem Speichern

### Schritt 3: Fehlermeldungen
- Freundliche Ablehnung bei ausländischen Nummern
- Erklärung dass nur deutsche Nummern akzeptiert werden
- Alternative vorschlagen (persönlich in Praxis kommen)

## Zu ändernde Dateien

### 1. src/dental/dental_tools.py
- [ ] Neue Funktion `ist_deutsche_telefonnummer()`
- [ ] Integration in `termin_direkt_buchen()`
- [ ] Anpassung der Fehlermeldungen

### 2. src/dental/appointment_manager.py
- [ ] Validierung in `termin_hinzufuegen()`
- [ ] Konsistente Fehlerbehandlung

### 3. src/agent/prompts.py (optional)
- [ ] Hinweis dass nur deutsche Nummern akzeptiert werden

## Validierungsregeln

### Gültige deutsche Nummern:
1. **Festnetz mit Vorwahl**:
   - Beginnt mit 0 + Vorwahl (2-5 Ziffern) + 4-8 Ziffern
   - Oder +49 + Vorwahl (ohne 0) + 4-8 Ziffern

2. **Mobilfunk**:
   - Beginnt mit 015x, 016x, 017x + 7-8 Ziffern
   - Oder +49 15x, +49 16x, +49 17x + 7-8 Ziffern

### Ungültige Nummern:
- Andere Ländercodes (+33, +44, +1, etc.)
- Zu kurze/lange Nummern
- Nummern ohne deutsche Vorwahl

## Beispiel-Implementierung

```python
import re

def ist_deutsche_telefonnummer(telefon: str) -> bool:
    # Entferne Leerzeichen, Bindestriche, Klammern
    nummer = re.sub(r'[\s\-\(\)]', '', telefon)
    
    # Deutsche Mobilnummer
    if re.match(r'^(\+49|0)1[567]\d{7,8}$', nummer):
        return True
    
    # Deutsche Festnetznummer
    if re.match(r'^(\+49|0)[2-9]\d{2,4}\d{4,8}$', nummer):
        return True
    
    return False
```

## Fehlerbehandlung

Bei ungültiger Nummer:
```
"Entschuldigung, wir können nur Termine für Patienten mit deutschen Telefonnummern vereinbaren. 
Bitte geben Sie eine deutsche Festnetz- oder Mobilnummer an, oder kommen Sie persönlich in die Praxis."
```

## Testing
- Deutsche Festnetznummern verschiedener Städte
- Deutsche Mobilnummern aller Anbieter
- Internationale Nummern (sollten abgelehnt werden)
- Falsch formatierte Nummern