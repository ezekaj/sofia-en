# 🏥 CRM-Dashboard - Zahnarztpraxis Dr. Weber

## 📋 Übersicht
Einfaches Web-CRM zur Anzeige Ihrer persönlichen Termine - **NICHT über Sofia, sondern direkt im Browser**.

## 🚀 Schnellstart

### Windows:
```bash
# 1. In den CRM-Ordner wechseln
cd crm

# 2. CRM starten
start_crm.bat
```

### Linux/Mac:
```bash
# 1. In den CRM-Ordner wechseln
cd crm

# 2. Pakete installieren
pip install -r requirements.txt

# 3. CRM starten
python app.py
```

## 🌐 Verwendung

1. **Öffnen Sie:** http://localhost:5000
2. **Geben Sie ein:** Ihren Namen oder Telefonnummer
3. **Wählen Sie:** Zeitraum (zukünftig, alle, vergangen)
4. **Sehen Sie:** Nur IHRE persönlichen Termine

## 🔒 Datenschutz

- ✅ **Nur Ihre Termine** - keine fremden Daten
- ✅ **Sichere Suche** - Name/Telefon erforderlich
- ✅ **Lokale Datenbank** - keine Cloud-Verbindung
- ✅ **Privat** - läuft nur auf Ihrem Computer

## 📱 Features

### 🎯 Terminübersicht
- **Datum & Uhrzeit** - übersichtlich sortiert
- **Behandlungsart** - was wird gemacht
- **Status** - bestätigt, abgesagt, etc.
- **Details** - vollständige Informationen

### 🔍 Flexible Suche
- **Nach Name** - Ihr vollständiger Name
- **Nach Telefon** - Ihre Telefonnummer
- **Zeiträume** - zukünftig, alle, vergangen

### 📊 Übersichtlich
- **Moderne Oberfläche** - responsive Design
- **Farbkodierung** - Status auf einen Blick
- **Mobile-freundlich** - funktioniert auf allen Geräten

## 🛠️ Technische Details

- **Framework:** Flask (Python)
- **Datenbank:** SQLite (../termine.db)
- **Frontend:** HTML5 + CSS3
- **Port:** 5000 (http://localhost:5000)

## 📞 Support

Bei Problemen:
1. Prüfen Sie, ob Python installiert ist
2. Stellen Sie sicher, dass die Datenbank `../termine.db` existiert
3. Kontaktieren Sie das Praxisteam

---
**© 2025 Zahnarztpraxis Dr. Weber - CRM Dashboard**
