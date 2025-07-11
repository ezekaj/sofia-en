#!/usr/bin/env python3
"""
🏥 EINFACHES CRM-DASHBOARD FÜR TERMINE
Zeigt Ihre persönlichen Termine in einer Web-Ansicht an
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Datenbank-Pfad
DB_PATH = "termine.db"

def get_db_connection():
    """Verbindung zur Datenbank herstellen"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Datenbank initialisieren falls nicht vorhanden"""
    if not os.path.exists(DB_PATH):
        conn = get_db_connection()
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()

@app.route('/')
def index():
    """Hauptseite - Login für Patientenname"""
    return render_template('login.html')

@app.route('/meine_termine')
def meine_termine():
    """Zeigt Ihre persönlichen Termine"""
    patient_name = request.args.get('patient_name', '')
    telefon = request.args.get('telefon', '')
    zeitraum = request.args.get('zeitraum', 'zukunft')
    
    if not patient_name and not telefon:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Zeitraum bestimmen
    heute = datetime.now().date()
    if zeitraum == 'zukunft':
        query = "SELECT * FROM termine WHERE (patient_name LIKE ? OR telefon LIKE ?) AND datum >= ? ORDER BY datum, uhrzeit"
        params = (f'%{patient_name}%', f'%{telefon}%', heute)
    elif zeitraum == 'alle':
        query = "SELECT * FROM termine WHERE (patient_name LIKE ? OR telefon LIKE ?) ORDER BY datum DESC, uhrzeit"
        params = (f'%{patient_name}%', f'%{telefon}%')
    elif zeitraum == 'vergangen':
        query = "SELECT * FROM termine WHERE (patient_name LIKE ? OR telefon LIKE ?) AND datum < ? ORDER BY datum DESC, uhrzeit"
        params = (f'%{patient_name}%', f'%{telefon}%', heute)
    else:
        query = "SELECT * FROM termine WHERE (patient_name LIKE ? OR telefon LIKE ?) AND datum >= ? ORDER BY datum, uhrzeit"
        params = (f'%{patient_name}%', f'%{telefon}%', heute)
    
    termine = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('termine.html', 
                         termine=termine, 
                         patient_name=patient_name,
                         telefon=telefon,
                         zeitraum=zeitraum,
                         heute=heute)

@app.route('/termin_details/<int:termin_id>')
def termin_details(termin_id):
    """Zeigt Details eines Termins"""
    conn = get_db_connection()
    termin = conn.execute('SELECT * FROM termine WHERE id = ?', (termin_id,)).fetchone()
    conn.close()
    
    if not termin:
        return "Termin nicht gefunden", 404
    
    return render_template('termin_details.html', termin=termin)

@app.route('/api/termine')
def api_termine():
    """API-Endpunkt für Termine (JSON)"""
    patient_name = request.args.get('patient_name', '')
    telefon = request.args.get('telefon', '')
    zeitraum = request.args.get('zeitraum', 'zukunft')
    
    conn = get_db_connection()
    
    heute = datetime.now().date()
    if zeitraum == 'zukunft':
        query = "SELECT * FROM termine WHERE (patient_name LIKE ? OR telefon LIKE ?) AND datum >= ? ORDER BY datum, uhrzeit"
        params = (f'%{patient_name}%', f'%{telefon}%', heute)
    elif zeitraum == 'alle':
        query = "SELECT * FROM termine WHERE (patient_name LIKE ? OR telefon LIKE ?) ORDER BY datum DESC, uhrzeit"
        params = (f'%{patient_name}%', f'%{telefon}%')
    else:
        query = "SELECT * FROM termine WHERE (patient_name LIKE ? OR telefon LIKE ?) AND datum >= ? ORDER BY datum, uhrzeit"
        params = (f'%{patient_name}%', f'%{telefon}%', heute)
    
    termine = conn.execute(query, params).fetchall()
    conn.close()
    
    # Konvertiere zu JSON-Format
    termine_list = []
    for termin in termine:
        termine_list.append({
            'id': termin['id'],
            'patient_name': termin['patient_name'],
            'telefon': termin['telefon'],
            'datum': termin['datum'],
            'uhrzeit': termin['uhrzeit'],
            'behandlungsart': termin['behandlungsart'],
            'beschreibung': termin['beschreibung'],
            'status': termin['status'],
            'notizen': termin['notizen']
        })
    
    return jsonify(termine_list)

if __name__ == '__main__':
    init_db()
    print("🏥 CRM-Dashboard startet...")
    print("📅 Öffnen Sie http://localhost:5000 in Ihrem Browser")
    print("👤 Geben Sie Ihren Namen ein, um Ihre Termine zu sehen")
    app.run(debug=True, host='0.0.0.0', port=5000)
