import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import logging

class AppointmentManager:
    def __init__(self, db_path: str = "termine.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialisiert die Terminverwaltung-Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Termine Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS termine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                telefon TEXT NOT NULL,
                email TEXT,
                datum DATE NOT NULL,
                uhrzeit TIME NOT NULL,
                behandlungsart TEXT NOT NULL,
                beschreibung TEXT,
                status TEXT DEFAULT 'bestätigt',
                notizen TEXT,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Patienten Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patienten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                telefon TEXT UNIQUE NOT NULL,
                email TEXT,
                geburtsdatum DATE,
                adresse TEXT,
                versicherung TEXT,
                notizen TEXT,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Terminverwaltung-Datenbank initialisiert")
    
    def termin_hinzufuegen(self, patient_name: str, telefon: str, datum: str,
                          uhrzeit: str, behandlungsart: str, email: str = "",
                          beschreibung: str = "", notizen: str = "") -> str:
        """
        Fügt einen neuen Termin hinzu
        ✅ VERHINDERT Termine in der Vergangenheit
        """
        try:
            # ✅ VERGANGENHEITS-PRÜFUNG: Explizite Validierung
            try:
                termin_datetime = datetime.strptime(f"{datum} {uhrzeit}", "%Y-%m-%d %H:%M")
                jetzt = datetime.now()

                if termin_datetime <= jetzt:
                    return f"❌ Der Termin am {datum} um {uhrzeit} liegt in der Vergangenheit. Bitte wählen Sie einen zukünftigen Termin."

            except ValueError:
                return f"❌ Ungültiges Datum- oder Zeitformat: {datum} {uhrzeit}"

            # Prüfe Verfügbarkeit (beinhaltet jetzt auch Vergangenheits-Prüfung)
            if not self.ist_verfuegbar(datum, uhrzeit):
                return f"❌ Termin am {datum} um {uhrzeit} ist nicht verfügbar"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO termine (patient_name, telefon, email, datum, uhrzeit, 
                                   behandlungsart, beschreibung, notizen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_name, telefon, email, datum, uhrzeit, behandlungsart, 
                  beschreibung, notizen))
            
            termin_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Füge Patient zur Datenbank hinzu falls noch nicht vorhanden
            self.patient_hinzufuegen(patient_name, telefon, email)
            
            return f"✅ Termin erfolgreich gebucht!\n📅 {datum} um {uhrzeit}\n👤 {patient_name}\n🦷 {behandlungsart}\n🆔 Termin-ID: {termin_id}"
            
        except Exception as e:
            logging.error(f"Fehler beim Hinzufügen des Termins: {e}")
            return f"❌ Fehler beim Buchen des Termins: {str(e)}"
    
    def ist_verfuegbar(self, datum: str, uhrzeit: str) -> bool:
        """
        Prüft ob ein Terminslot verfügbar ist
        ✅ VERHINDERT Termine in der Vergangenheit
        """
        try:
            # ✅ VERGANGENHEITS-PRÜFUNG: Keine Termine in der Vergangenheit
            termin_datetime = datetime.strptime(f"{datum} {uhrzeit}", "%Y-%m-%d %H:%M")
            jetzt = datetime.now()

            if termin_datetime <= jetzt:
                return False  # Termine in Vergangenheit sind NICHT verfügbar

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) FROM termine
                WHERE datum = ? AND uhrzeit = ? AND status = 'bestätigt'
            ''', (datum, uhrzeit))

            count = cursor.fetchone()[0]
            conn.close()

            return count == 0

        except ValueError:
            # Ungültiges Datum/Zeit-Format
            return False
    
    def get_verfuegbare_termine(self, ab_datum: str = "", anzahl: int = 10) -> List[Dict]:
        """Findet die nächsten verfügbaren Termine"""
        if not ab_datum:
            ab_datum = datetime.now().strftime('%Y-%m-%d')
        
        start_datum = datetime.strptime(ab_datum, '%Y-%m-%d')
        verfuegbare_termine = []
        
        # Arbeitszeiten definieren
        arbeitszeiten = {
            0: ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"],  # Montag
            1: ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"],  # Dienstag
            2: ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"],  # Mittwoch
            3: ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"],  # Donnerstag
            4: ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"],  # Freitag
            5: ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30"],  # Samstag
        }
        
        # Suche in den nächsten 30 Tagen
        for tage_voraus in range(30):
            aktuelles_datum = start_datum + timedelta(days=tage_voraus)
            wochentag = aktuelles_datum.weekday()
            
            # Überspringe Sonntag
            if wochentag == 6:
                continue
            
            datum_str = aktuelles_datum.strftime('%Y-%m-%d')
            tageszeiten = arbeitszeiten.get(wochentag, [])
            
            for zeit in tageszeiten:
                if self.ist_verfuegbar(datum_str, zeit):
                    tag_name = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"][wochentag]
                    
                    verfuegbare_termine.append({
                        "datum": datum_str,
                        "uhrzeit": zeit,
                        "wochentag": tag_name,
                        "anzeige": f"{tag_name}, {aktuelles_datum.strftime('%d.%m.%Y')} um {zeit} Uhr"
                    })
                    
                    if len(verfuegbare_termine) >= anzahl:
                        return verfuegbare_termine
        
        return verfuegbare_termine
    
    def get_tagesplan(self, datum: str, fuer_arzt: bool = False) -> str:
        """Zeigt den Tagesplan für einen bestimmten Tag"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM termine 
                WHERE datum = ? AND status = 'bestätigt'
                ORDER BY uhrzeit
            ''', (datum,))
            
            termine = cursor.fetchall()
            conn.close()
            
            if not termine:
                if fuer_arzt:
                    return f"📅 **Tagesplan für {datum}**\n\n✅ Keine Termine heute - Freier Tag!"
                else:
                    return f"Für {datum} sind viele Termine verfügbar. Wann passt es Ihnen am besten?"
            
            if fuer_arzt:
                # Detaillierte Arztansicht
                plan = f"📅 **Tagesplan für {datum}**\n\n"
                plan += f"👥 **Anzahl Patienten:** {len(termine)}\n\n"
                
                for i, termin in enumerate(termine, 1):
                    plan += f"**{i}. {termin[5]} Uhr** - {termin[7]}\n"  # uhrzeit, behandlungsart
                    plan += f"   👤 Patient: {termin[1]}\n"  # patient_name
                    plan += f"   📞 Telefon: {termin[2]}\n"  # telefon
                    plan += f"   🦷 Behandlung: {termin[7]}\n"  # behandlungsart
                    plan += f"   📝 Beschreibung: {termin[8] or 'Keine'}\n"  # beschreibung
                    plan += f"   📋 Notizen: {termin[10] or 'Keine'}\n"  # notizen
                    plan += f"   🆔 Termin-ID: {termin[0]}\n\n"  # id
                
                return plan
            else:
                # Vereinfachte Patientenansicht
                belegte_zeiten = [termin[5] for termin in termine]  # uhrzeit
                return f"Für {datum} sind folgende Zeiten bereits belegt: {', '.join(belegte_zeiten)}"
                
        except Exception as e:
            logging.error(f"Fehler beim Abrufen des Tagesplans: {e}")
            return "❌ Fehler beim Abrufen des Tagesplans"
    
    def get_wochenuebersicht(self, start_datum: str, fuer_arzt: bool = False) -> str:
        """Zeigt die Wochenübersicht der Termine"""
        try:
            start = datetime.strptime(start_datum, '%Y-%m-%d')
            montag = start - timedelta(days=start.weekday())
            
            uebersicht = f"📅 **Wochenübersicht ab {montag.strftime('%d.%m.%Y')}**\n\n"
            gesamt_termine = 0
            
            for tag in range(7):
                aktuelles_datum = montag + timedelta(days=tag)
                datum_str = aktuelles_datum.strftime('%Y-%m-%d')
                tag_name = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][tag]
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM termine 
                    WHERE datum = ? AND status = 'bestätigt'
                    ORDER BY uhrzeit
                ''', (datum_str,))
                termine = cursor.fetchall()
                conn.close()
                
                if fuer_arzt:
                    uebersicht += f"**{tag_name} ({aktuelles_datum.strftime('%d.%m')})**\n"
                    
                    if aktuelles_datum.weekday() == 6:  # Sonntag
                        uebersicht += "   🚫 Praxis geschlossen\n\n"
                    elif not termine:
                        uebersicht += "   ✅ Keine Termine - Freier Tag\n\n"
                    else:
                        gesamt_termine += len(termine)
                        uebersicht += f"   👥 {len(termine)} Termine:\n"
                        for termin in termine:
                            uebersicht += f"      • {termin[5]} - {termin[1]} ({termin[7]})\n"
                        uebersicht += "\n"
                else:
                    if aktuelles_datum.weekday() == 6:  # Sonntag
                        continue
                    
                    verfuegbare_slots = self.get_verfuegbare_termine_tag(datum_str)
                    if verfuegbare_slots:
                        uebersicht += f"**{tag_name} ({aktuelles_datum.strftime('%d.%m')})**\n"
                        uebersicht += f"   ✅ {len(verfuegbare_slots)} Termine verfügbar\n\n"
            
            if fuer_arzt:
                uebersicht += f"📊 **Wochenstatistik:**\n"
                uebersicht += f"   • Gesamte Termine: {gesamt_termine}\n"
                uebersicht += f"   • Durchschnitt pro Tag: {gesamt_termine/5:.1f}\n"
            
            return uebersicht
            
        except Exception as e:
            logging.error(f"Fehler bei Wochenübersicht: {e}")
            return "❌ Fehler bei der Wochenübersicht"
    
    def get_verfuegbare_termine_tag(self, datum: str) -> List[str]:
        """Gibt verfügbare Termine für einen Tag zurück"""
        wochentag = datetime.strptime(datum, '%Y-%m-%d').weekday()
        
        if wochentag == 5:  # Samstag
            alle_slots = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30"]
        elif wochentag == 6:  # Sonntag
            return []
        else:
            alle_slots = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", 
                         "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]
        
        verfuegbare_slots = []
        for slot in alle_slots:
            if self.ist_verfuegbar(datum, slot):
                verfuegbare_slots.append(slot)
        
        return verfuegbare_slots
    
    def termin_suchen(self, suchbegriff: str, zeitraum: str = "naechste_woche") -> str:
        """Sucht nach Terminen basierend auf verschiedenen Kriterien"""
        try:
            heute = datetime.now()
            
            if zeitraum == "heute":
                start_datum = heute
                end_datum = heute
            elif zeitraum == "morgen":
                start_datum = heute + timedelta(days=1)
                end_datum = heute + timedelta(days=1)
            elif zeitraum == "naechste_woche":
                start_datum = heute
                end_datum = heute + timedelta(days=7)
            elif zeitraum == "naechster_monat":
                start_datum = heute
                end_datum = heute + timedelta(days=30)
            else:
                start_datum = heute
                end_datum = heute + timedelta(days=7)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM termine 
                WHERE (patient_name LIKE ? OR telefon LIKE ? OR behandlungsart LIKE ?)
                AND datum >= ? AND datum <= ?
                AND status = 'bestätigt'
                ORDER BY datum, uhrzeit
            ''', (f'%{suchbegriff}%', f'%{suchbegriff}%', f'%{suchbegriff}%',
                  start_datum.strftime('%Y-%m-%d'), end_datum.strftime('%Y-%m-%d')))
            
            gefundene_termine = cursor.fetchall()
            conn.close()
            
            if not gefundene_termine:
                return f"🔍 Keine Termine gefunden für '{suchbegriff}' im angegebenen Zeitraum."
            
            ergebnis = f"🔍 **Suchergebnisse für '{suchbegriff}'** ({len(gefundene_termine)} Termine gefunden):\n\n"
            
            for i, termin in enumerate(gefundene_termine, 1):
                ergebnis += f"{i}. **{termin[4]} um {termin[5]}**\n"  # datum, uhrzeit
                ergebnis += f"   👤 Patient: {termin[1]}\n"  # patient_name
                ergebnis += f"   📞 Telefon: {termin[2]}\n"  # telefon
                ergebnis += f"   🦷 Behandlung: {termin[7]}\n"  # behandlungsart
                ergebnis += f"   📊 Status: {termin[9]}\n"  # status
                ergebnis += f"   🆔 Termin-ID: {termin[0]}\n\n"  # id
            
            return ergebnis
            
        except Exception as e:
            logging.error(f"Fehler bei der Terminsuche: {e}")
            return "❌ Fehler bei der Terminsuche"
    
    def get_patientenhistorie(self, telefon: str) -> str:
        """Zeigt die Terminhistorie eines Patienten"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hole Patienteninfo
            cursor.execute('SELECT * FROM patienten WHERE telefon = ?', (telefon,))
            patient = cursor.fetchone()
            
            # Hole Terminhistorie
            cursor.execute('''
                SELECT * FROM termine 
                WHERE telefon = ?
                ORDER BY datum DESC, uhrzeit DESC
            ''', (telefon,))
            termine = cursor.fetchall()
            
            conn.close()
            
            if not patient:
                return f"❌ Patient mit Telefon {telefon} nicht in der Datenbank gefunden."
            
            historie = f"📋 **Patientenhistorie - {patient[1]}**\n\n"  # name
            historie += f"📞 Telefon: {telefon}\n"
            historie += f"📧 Email: {patient[3] or 'Nicht verfügbar'}\n"
            historie += f"🎂 Geburtsdatum: {patient[4] or 'Nicht verfügbar'}\n\n"
            
            if not termine:
                historie += "📅 Keine Termine in der Historie gefunden.\n"
                return historie
            
            historie += f"🗓️ **Terminhistorie ({len(termine)} Termine):**\n\n"
            
            for i, termin in enumerate(termine, 1):
                status_icon = "✅" if termin[9] == 'bestätigt' else "❌"  # status
                historie += f"{i}. {status_icon} {termin[4]} um {termin[5]}\n"  # datum, uhrzeit
                historie += f"   🦷 {termin[7]}\n"  # behandlungsart
                historie += f"   📝 {termin[8] or 'Keine Beschreibung'}\n"  # beschreibung
                historie += f"   📋 {termin[10] or 'Keine Notizen'}\n\n"  # notizen
            
            return historie
            
        except Exception as e:
            logging.error(f"Fehler bei Patientenhistorie: {e}")
            return "❌ Fehler beim Abrufen der Patientenhistorie"
    
    def patient_hinzufuegen(self, name: str, telefon: str, email: str = "", 
                           geburtsdatum: str = "", adresse: str = "", 
                           versicherung: str = "", notizen: str = "") -> bool:
        """Fügt einen Patienten zur Datenbank hinzu"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prüfe ob Patient bereits existiert
            cursor.execute('SELECT id FROM patienten WHERE telefon = ?', (telefon,))
            if cursor.fetchone():
                conn.close()
                return True  # Patient existiert bereits
            
            cursor.execute('''
                INSERT INTO patienten (name, telefon, email, geburtsdatum, adresse, versicherung, notizen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, telefon, email, geburtsdatum, adresse, versicherung, notizen))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Fehler beim Hinzufügen des Patienten: {e}")
            return False
    
    def termin_absagen(self, termin_id: int, grund: str = "") -> str:
        """Sagt einen Termin ab"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE termine 
                SET status = 'abgesagt', 
                    notizen = CASE 
                        WHEN notizen IS NULL OR notizen = '' THEN ?
                        ELSE notizen || ' | Absagegrund: ' || ?
                    END,
                    aktualisiert_am = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (f'Absagegrund: {grund}', grund, termin_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return f"✅ Termin {termin_id} wurde erfolgreich abgesagt."
            else:
                conn.close()
                return f"❌ Termin {termin_id} nicht gefunden."
                
        except Exception as e:
            logging.error(f"Fehler beim Absagen des Termins: {e}")
            return f"❌ Fehler beim Absagen des Termins: {str(e)}"
    
    def get_statistiken(self, zeitraum: str = "diese_woche") -> str:
        """Zeigt Statistiken für die Praxis"""
        try:
            heute = datetime.now()
            
            if zeitraum == "heute":
                start_datum = heute
                end_datum = heute
                zeitraum_name = "heute"
            elif zeitraum == "diese_woche":
                start_datum = heute - timedelta(days=heute.weekday())
                end_datum = start_datum + timedelta(days=6)
                zeitraum_name = "diese Woche"
            elif zeitraum == "diesen_monat":
                start_datum = heute.replace(day=1)
                end_datum = heute
                zeitraum_name = "diesen Monat"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as gesamt,
                    SUM(CASE WHEN status = 'bestätigt' THEN 1 ELSE 0 END) as bestätigt,
                    SUM(CASE WHEN status = 'abgesagt' THEN 1 ELSE 0 END) as abgesagt,
                    behandlungsart
                FROM termine 
                WHERE datum >= ? AND datum <= ?
                GROUP BY behandlungsart
            ''', (start_datum.strftime('%Y-%m-%d'), end_datum.strftime('%Y-%m-%d')))
            
            behandlungsarten = cursor.fetchall()
            
            # Gesamtstatistiken
            cursor.execute('''
                SELECT 
                    COUNT(*) as gesamt,
                    SUM(CASE WHEN status = 'bestätigt' THEN 1 ELSE 0 END) as bestätigt,
                    SUM(CASE WHEN status = 'abgesagt' THEN 1 ELSE 0 END) as abgesagt
                FROM termine 
                WHERE datum >= ? AND datum <= ?
            ''', (start_datum.strftime('%Y-%m-%d'), end_datum.strftime('%Y-%m-%d')))
            
            gesamt_stats = cursor.fetchone()
            conn.close()
            
            stats = f"📊 **Praxisstatistiken für {zeitraum_name}:**\n\n"
            stats += f"📅 **Terminübersicht:**\n"
            stats += f"   • Gesamte Termine: {gesamt_stats[0]}\n"
            stats += f"   • Bestätigte Termine: {gesamt_stats[1]}\n"
            stats += f"   • Abgesagte Termine: {gesamt_stats[2]}\n\n"
            
            if behandlungsarten:
                stats += f"🦷 **Behandlungsarten:**\n"
                for behandlung in behandlungsarten:
                    stats += f"   • {behandlung[3]}: {behandlung[0]} Termine\n"
            
            # Auslastung berechnen
            arbeitstage = sum(1 for d in range((end_datum - start_datum).days + 1) 
                            if (start_datum + timedelta(days=d)).weekday() < 6)
            
            if arbeitstage > 0:
                durchschnitt = gesamt_stats[0] / arbeitstage
                stats += f"\n📈 **Auslastung:**\n"
                stats += f"   • Durchschnitt pro Tag: {durchschnitt:.1f} Termine\n"
                stats += f"   • Arbeitstage: {arbeitstage}\n"
            
            return stats
            
        except Exception as e:
            logging.error(f"Fehler bei Statistiken: {e}")
            return "❌ Fehler beim Abrufen der Statistiken"
    
    def parse_natural_language(self, text: str) -> tuple:
        """Erweiterte Erkennung von Terminen aus natürlicher Sprache mit KI-Integration"""
        text = text.lower()
        jetzt = datetime.now()
        datetime_info = self.get_current_datetime_info()
        
        # Datum erkennen - viel intelligenter mit KI-Kontext
        datum = datetime_info["aktuelles_datum"]
        
        # Relative Datumsangaben
        if 'heute' in text:
            datum = datetime_info["aktuelles_datum"]
        elif 'morgen' in text:
            datum = datetime_info["morgen"]
        elif 'übermorgen' in text:
            datum = datetime_info["übermorgen"]
        elif 'nächste woche' in text or 'kommende woche' in text:
            datum = datetime_info["nächste_woche"]
        elif 'nächsten montag' in text:
            tage_bis_montag = (7 - jetzt.weekday()) % 7
            if tage_bis_montag == 0:
                tage_bis_montag = 7
            datum = (jetzt + timedelta(days=tage_bis_montag)).strftime('%Y-%m-%d')
        elif 'nächsten dienstag' in text:
            tage_bis_dienstag = (8 - jetzt.weekday()) % 7
            if tage_bis_dienstag == 0:
                tage_bis_dienstag = 7
            datum = (jetzt + timedelta(days=tage_bis_dienstag)).strftime('%Y-%m-%d')
        elif 'nächsten mittwoch' in text:
            tage_bis_mittwoch = (9 - jetzt.weekday()) % 7
            if tage_bis_mittwoch == 0:
                tage_bis_mittwoch = 7
            datum = (jetzt + timedelta(days=tage_bis_mittwoch)).strftime('%Y-%m-%d')
        elif 'nächsten donnerstag' in text:
            tage_bis_donnerstag = (10 - jetzt.weekday()) % 7
            if tage_bis_donnerstag == 0:
                tage_bis_donnerstag = 7
            datum = (jetzt + timedelta(days=tage_bis_donnerstag)).strftime('%Y-%m-%d')
        elif 'nächsten freitag' in text:
            tage_bis_freitag = (11 - jetzt.weekday()) % 7
            if tage_bis_freitag == 0:
                tage_bis_freitag = 7
            datum = (jetzt + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')
        elif 'nächsten samstag' in text:
            tage_bis_samstag = (12 - jetzt.weekday()) % 7
            if tage_bis_samstag == 0:
                tage_bis_samstag = 7
            datum = (jetzt + timedelta(days=tage_bis_samstag)).strftime('%Y-%m-%d')
        
        # Spezifische Datumsangaben (z.B. "am 15.07" oder "15.07.2025")
        datum_match = re.search(r'(\d{1,2})\.(\d{1,2})\.?(\d{4})?', text)
        if datum_match:
            tag = int(datum_match.group(1))
            monat = int(datum_match.group(2))
            jahr = int(datum_match.group(3)) if datum_match.group(3) else jetzt.year
            
            try:
                datum = datetime(jahr, monat, tag).strftime('%Y-%m-%d')
            except ValueError:
                pass  # Ungültiges Datum, Standard beibehalten
        
        # Uhrzeit erkennen - erweitert
        uhrzeit = None
        
        # Verschiedene Uhrzeitformate
        zeit_patterns = [
            r'(\d{1,2}):(\d{2})',  # 14:30
            r'(\d{1,2}) uhr',      # 14 uhr
            r'um (\d{1,2})',       # um 14
            r'(\d{1,2})\.(\d{2})', # 14.30
        ]
        
        for pattern in zeit_patterns:
            zeit_match = re.search(pattern, text)
            if zeit_match:
                if ':' in pattern or '\.' in pattern:
                    stunde = int(zeit_match.group(1))
                    minute = int(zeit_match.group(2))
                else:
                    stunde = int(zeit_match.group(1))
                    minute = 0
                
                # Validierung
                if 0 <= stunde <= 23 and 0 <= minute <= 59:
                    uhrzeit = f"{stunde:02d}:{minute:02d}"
                    break
        
        # Relative Uhrzeiten basierend auf Praxiszeiten
        if not uhrzeit:
            if 'vormittag' in text:
                uhrzeit = "10:00"
            elif 'nachmittag' in text:
                uhrzeit = "15:00"
            elif 'früh' in text:
                uhrzeit = "09:00"
            elif 'spät' in text:
                uhrzeit = "17:00"
            elif 'mittag' in text:
                uhrzeit = "12:00"
        
        # Behandlungsart erkennen - erweitert
        behandlungsarten = {
            'kontrolle': 'Kontrolluntersuchung',
            'kontrolluntersuchung': 'Kontrolluntersuchung',
            'vorsorge': 'Kontrolluntersuchung',
            'check': 'Kontrolluntersuchung',
            'reinigung': 'Professionelle Zahnreinigung',
            'zahnreinigung': 'Professionelle Zahnreinigung',
            'pzr': 'Professionelle Zahnreinigung',
            'prophylaxe': 'Professionelle Zahnreinigung',
            'hygiene': 'Professionelle Zahnreinigung',
            'füllung': 'Füllungstherapie',
            'plombe': 'Füllungstherapie',
            'loch': 'Füllungstherapie',
            'wurzel': 'Wurzelbehandlung',
            'wurzelbehandlung': 'Wurzelbehandlung',
            'endodontie': 'Wurzelbehandlung',
            'implantat': 'Implantat',
            'implantation': 'Implantat',
            'krone': 'Kronen/Brücken',
            'brücke': 'Kronen/Brücken',
            'zahnersatz': 'Kronen/Brücken',
            'notfall': 'Notfalltermin',
            'schmerz': 'Notfalltermin',
            'schmerzen': 'Notfalltermin',
            'akut': 'Notfalltermin',
            'dringend': 'Notfalltermin',
            'beratung': 'Beratungstermin',
            'erstberatung': 'Beratungstermin',
            'erstuntersuchung': 'Erstuntersuchung',
            'bleaching': 'Bleaching',
            'aufhellung': 'Bleaching',
            'weißmachen': 'Bleaching',
            'weisheitszahn': 'Chirurgie',
            'extraktion': 'Chirurgie',
            'ziehen': 'Chirurgie',
            'zahnspange': 'Kieferorthopädie',
            'brackets': 'Kieferorthopädie',
            'spange': 'Kieferorthopädie'
        }
        
        behandlungsart = 'Kontrolluntersuchung'  # Standard
        for schluessel, wert in behandlungsarten.items():
            if schluessel in text:
                behandlungsart = wert
                break
        
        # Titel extrahieren (bereinigt)
        titel = text
        entfernen = ['heute', 'morgen', 'übermorgen', 'nächste woche', 'kommende woche',
                    'nächsten montag', 'nächsten dienstag', 'nächsten mittwoch',
                    'nächsten donnerstag', 'nächsten freitag', 'nächsten samstag',
                    'um', 'uhr', 'vormittag', 'nachmittag', 'früh', 'spät', 'mittag']
        
        if uhrzeit:
            entfernen.append(uhrzeit)
        
        for keyword in entfernen:
            titel = titel.replace(keyword, '').strip()
        
        # Zusätzliche Kontextinformationen
        kontext = {
            "ist_heute_arbeitstag": datetime_info["ist_heute_arbeitstag"],
            "praxis_offen": datetime_info["praxis_offen"],
            "aktueller_wochentag": datetime_info["wochentag"],
            "arbeitszeiten_heute": datetime_info["arbeitszeiten_heute"]
        }
        
        return titel, datum, uhrzeit, behandlungsart, kontext
    
    def get_current_datetime_info(self) -> Dict:
        """
        ✅ REPARIERT: Verwendet die zentrale get_current_datetime_info() Funktion
        Verhindert Datums-Inkonsistenzen zwischen verschiedenen Modulen
        """
        from .dental_tools import get_current_datetime_info

        # Verwende die zentrale Funktion
        zentrale_info = get_current_datetime_info()

        # Erweitere um appointment_manager spezifische Informationen
        jetzt = zentrale_info['datetime']

        # Kombiniere zentrale Info mit lokalen Erweiterungen
        erweiterte_info = zentrale_info.copy()
        erweiterte_info.update({
            # Zusätzliche appointment_manager spezifische Felder
            "aktuelles_datum": zentrale_info['date_iso'],
            "aktuelle_uhrzeit": zentrale_info['time_formatted'],
            "wochentag": zentrale_info['weekday'],
            "wochentag_nummer": zentrale_info['weekday_number'],
            "tag": zentrale_info['day'],
            "monat": zentrale_info['month'],
            "jahr": zentrale_info['year'],
            "kalenderwoche": zentrale_info['week_number'],
            "ist_wochenende": zentrale_info['is_weekend'],
            "ist_arbeitstag": zentrale_info['is_workday'],
            "morgen": zentrale_info['tomorrow_iso'],
            "übermorgen": (jetzt + timedelta(days=2)).strftime('%Y-%m-%d'),
            # ✅ KORREKTE "nächste Woche" Berechnung - nächster Montag
            "nächste_woche": self._berechne_naechste_woche(jetzt).strftime('%Y-%m-%d'),
            "formatiert": zentrale_info['date_time_formatted'],
            "formatiert_lang": zentrale_info['date_time_long'],
            "ist_heute_arbeitstag": zentrale_info['is_workday'],
            "praxis_offen": self.ist_praxis_offen(jetzt),
            "arbeitszeiten_heute": self.get_arbeitszeiten_heute(jetzt.weekday())
        })

        return erweiterte_info

    def _berechne_naechste_woche(self, jetzt: datetime) -> datetime:
        """
        ✅ KORREKTE Berechnung der nächsten Woche = nächster Montag
        Nicht einfach +7 Tage, sondern der tatsächliche nächste Montag
        """
        # Tage bis zum nächsten Montag berechnen
        tage_bis_naechster_montag = (7 - jetzt.weekday()) % 7
        if tage_bis_naechster_montag == 0:  # Heute ist Montag
            tage_bis_naechster_montag = 7  # Nächster Montag

        return jetzt + timedelta(days=tage_bis_naechster_montag)

    def ist_praxis_offen(self, datum_zeit: datetime) -> bool:
        """Prüft ob die Praxis zu einer bestimmten Zeit geöffnet ist"""
        wochentag = datum_zeit.weekday()
        stunde = datum_zeit.hour
        minute = datum_zeit.minute
        aktuelle_zeit = stunde * 60 + minute
        
        # Sonntag = geschlossen
        if wochentag == 6:
            return False
        
        # Montag-Freitag: 9:00-11:30, 14:00-17:30
        if wochentag <= 4:
            return (9 * 60 <= aktuelle_zeit <= 11 * 60 + 30) or (14 * 60 <= aktuelle_zeit <= 17 * 60 + 30)
        
        # Samstag: 9:00-12:30
        if wochentag == 5:
            return 9 * 60 <= aktuelle_zeit <= 12 * 60 + 30
        
        return False
    
    def get_arbeitszeiten_heute(self, wochentag: int) -> Dict:
        """Gibt die Arbeitszeiten für einen bestimmten Wochentag zurück"""
        arbeitszeiten = {
            0: {"vormittag": "09:00-11:30", "nachmittag": "14:00-17:30"},  # Montag
            1: {"vormittag": "09:00-11:30", "nachmittag": "14:00-17:30"},  # Dienstag
            2: {"vormittag": "09:00-11:30", "nachmittag": "14:00-17:30"},  # Mittwoch
            3: {"vormittag": "09:00-11:30", "nachmittag": "14:00-17:30"},  # Donnerstag
            4: {"vormittag": "09:00-11:30", "nachmittag": "14:00-17:30"},  # Freitag
            5: {"vormittag": "09:00-12:30", "nachmittag": ""},             # Samstag
            6: {"vormittag": "", "nachmittag": ""}                         # Sonntag
        }
        return arbeitszeiten.get(wochentag, {"vormittag": "", "nachmittag": ""})
    
    def get_intelligente_terminvorschlaege(self, behandlungsart: str = "Kontrolluntersuchung", 
                                         ab_datum: str = "", anzahl: int = 5) -> str:
        """Gibt intelligente Terminvorschläge basierend auf aktuellem Datum/Zeit"""
        jetzt = datetime.now()
        datetime_info = self.get_current_datetime_info()
        
        # Bestimme Startdatum intelligent
        if not ab_datum:
            # Wenn es noch früh am Tag ist, schlage heute vor
            if jetzt.hour < 12 and datetime_info["ist_arbeitstag"] and datetime_info["praxis_offen"]:
                ab_datum = datetime_info["aktuelles_datum"]
            else:
                # Sonst ab morgen
                ab_datum = datetime_info["morgen"]
        
        verfuegbare_termine = self.get_verfuegbare_termine(ab_datum, anzahl)
        
        if not verfuegbare_termine:
            return f"🔍 Leider keine Termine in nächster Zeit verfügbar für {behandlungsart}."
        
        # Intelligente Antwort basierend auf aktuellem Kontext
        antwort = f"🗓️ **Terminvorschläge für {behandlungsart}**\n\n"
        antwort += f"📅 Heute ist {datetime_info['wochentag']}, {datetime_info['formatiert']}\n"
        
        if datetime_info["ist_heute_arbeitstag"]:
            antwort += f"🏥 Praxis heute geöffnet: {datetime_info['arbeitszeiten_heute']['vormittag']}"
            if datetime_info['arbeitszeiten_heute']['nachmittag']:
                antwort += f", {datetime_info['arbeitszeiten_heute']['nachmittag']}"
            antwort += "\n"
        
        antwort += f"\n✅ **Nächste {len(verfuegbare_termine)} verfügbare Termine:**\n\n"
        
        for i, termin in enumerate(verfuegbare_termine, 1):
            # Zusätzliche Informationen je nach Zeitpunkt
            termin_datum = datetime.strptime(termin['datum'], '%Y-%m-%d')
            tage_differenz = (termin_datum - jetzt).days
            
            if tage_differenz == 0:
                zeit_info = " (heute)"
            elif tage_differenz == 1:
                zeit_info = " (morgen)"
            elif tage_differenz == 2:
                zeit_info = " (übermorgen)"
            elif tage_differenz <= 7:
                zeit_info = f" (in {tage_differenz} Tagen)"
            else:
                zeit_info = f" (in {tage_differenz} Tagen)"
            
            antwort += f"{i}. {termin['anzeige']}{zeit_info}\n"
        
        antwort += f"\n💡 **Welcher Termin passt Ihnen am besten?**"
        
        return antwort

# Globale Instanz
appointment_manager = AppointmentManager()
