# 🔐 Privates Repository - Sicherheitsanleitung

## Warum privat?

Das ELO German Repository ist als **privates Repository** konfiguriert aus folgenden Gründen:

### 🛡️ Sicherheit
- **API-Keys**: LiveKit und Google AI Credentials bleiben geschützt
- **Praxisdaten**: Zahnarztpraxis-Informationen sind vertraulich
- **Geschäftsdaten**: Preise, Termine und interne Abläufe

### 📋 Datenschutz
- **DSGVO-Konformität**: Patientendaten und Praxisinfos geschützt
- **Geschäftsgeheimnisse**: Interne Prozesse und Konfigurationen
- **Professionelle Nutzung**: Seriöse Geschäftsanwendung

## Zugriffsverwaltung

### Repository-Besitzer
- **Vollzugriff**: Alle Funktionen und Einstellungen
- **Collaborator-Verwaltung**: Kann andere Personen einladen
- **Sicherheitseinstellungen**: Verwaltet Zugriff und Berechtigungen

### Collaborators hinzufügen
1. Gehen Sie zu Ihrem Repository auf GitHub
2. Klicken Sie auf "Settings" (Einstellungen)
3. Klicken Sie auf "Collaborators" (Mitarbeiter)
4. Klicken Sie "Add people" (Personen hinzufügen)
5. Geben Sie GitHub-Benutzername oder E-Mail ein
6. Wählen Sie Berechtigungsstufe:
   - **Read**: Nur lesen und klonen
   - **Write**: Lesen, klonen und committen
   - **Admin**: Vollzugriff wie Besitzer

## Sicherheits-Checkliste

### ✅ Bereits konfiguriert:
- [x] `.env` Dateien in .gitignore
- [x] Keine API-Keys im Code
- [x] Private Repository-Einstellung
- [x] Sensible Daten ausgeschlossen

### 🔧 Empfohlene Zusatzmaßnahmen:
- [ ] **2FA aktivieren**: Zwei-Faktor-Authentifizierung für GitHub
- [ ] **Branch Protection**: Schutz des main-Branches
- [ ] **Code Reviews**: Änderungen nur nach Review
- [ ] **Secrets Management**: GitHub Secrets für CI/CD

## Deployment-Sicherheit

### Produktionsumgebung:
```bash
# Niemals diese Befehle in öffentlichen Logs
export LIVEKIT_API_KEY="your-secret-key"
export GOOGLE_API_KEY="your-secret-key"

# Verwenden Sie stattdessen sichere Secrets-Management
```

### Sichere Practices:
1. **Separate Credentials**: Entwicklung vs. Produktion
2. **Regelmäßige Rotation**: API-Keys regelmäßig erneuern
3. **Logging**: Keine Credentials in Logs
4. **Backups**: Sichere Datensicherung

## Team-Collaboration

### Für Entwickler:
```bash
# Repository klonen (nur mit Berechtigung)
git clone https://github.com/IHRUSERNAME/elo-german.git

# Eigene .env Datei erstellen
cp .env.example .env
# API-Keys eintragen
```

### Für Praxispersonal:
- **Kein direkter Code-Zugriff nötig**
- **Nur finale Anwendung verwenden**
- **Schulung für Bedienung der Assistentin**

## Rechtliche Hinweise

### Datenschutz (DSGVO):
- Patientendaten niemals in Git speichern
- Nur notwendige Praxisdaten verwenden
- Regelmäßige Sicherheitsaudits

### Lizenzierung:
- Code ist Eigentum des Repository-Besitzers
- Verwendung nur nach Berechtigung
- Kommerzielle Nutzung nach Absprache

## Notfallplan

### Bei Sicherheitsproblemen:
1. **Sofort**: Repository temporär privat stellen
2. **API-Keys**: Alle Credentials sofort deaktivieren
3. **Logs prüfen**: Unauthorized access kontrollieren
4. **Neue Keys**: Frische Credentials generieren
5. **Team informieren**: Alle Beteiligten benachrichtigen

### Kontakt:
- **Repository-Besitzer**: [Ihre E-Mail]
- **IT-Support**: [Support-Kontakt]
- **Notfall**: [Notfall-Telefon]

---

🔒 **Sicherheit geht vor** - Vielen Dank für verantwortungsvolle Nutzung!
