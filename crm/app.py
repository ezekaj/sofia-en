#!/usr/bin/env python3
"""
🏥 EINFACHES CRM-DASHBOARD FÜR IHRE TERMINE
Zeigt Ihre persönlichen Termine in einer Web-Ansicht an
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Datenbank-Pfad (zeigt auf die Hauptdatenbank)
DB_PATH = "../termine.db"

def get_db_connection():
    """Verbindung zur Datenbank herstellen"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Hauptseite - CRM Dashboard Übersicht"""
    return render_template('dashboard.html')

@app.route('/login')
def login():
    """Login für persönliche Termine"""
    return render_template('login.html')

@app.route('/alle_termine')
def alle_termine():
    """Zeigt ALLE Termine im System - Vollständiges CRM"""
    zeitraum = request.args.get('zeitraum', 'alle')
    sortierung = request.args.get('sortierung', 'datum_desc')

    conn = get_db_connection()

    # Zeitraum bestimmen
    heute = datetime.now().date()
    if zeitraum == 'heute':
        query = "SELECT * FROM termine WHERE datum = ?"
        params = (heute,)
    elif zeitraum == 'zukunft':
        query = "SELECT * FROM termine WHERE datum >= ?"
        params = (heute,)
    elif zeitraum == 'vergangen':
        query = "SELECT * FROM termine WHERE datum < ?"
        params = (heute,)
    elif zeitraum == 'diese_woche':
        woche_start = heute - timedelta(days=heute.weekday())
        woche_ende = woche_start + timedelta(days=6)
        query = "SELECT * FROM termine WHERE datum BETWEEN ? AND ?"
        params = (woche_start, woche_ende)
    else:  # alle
        query = "SELECT * FROM termine"
        params = ()

    # Sortierung hinzufügen
    if sortierung == 'datum_asc':
        query += " ORDER BY datum ASC, uhrzeit ASC"
    elif sortierung == 'datum_desc':
        query += " ORDER BY datum DESC, uhrzeit DESC"
    elif sortierung == 'name':
        query += " ORDER BY patient_name ASC, datum ASC"
    elif sortierung == 'status':
        query += " ORDER BY status ASC, datum ASC"
    else:
        query += " ORDER BY datum DESC, uhrzeit DESC"

    termine = conn.execute(query, params).fetchall()
    conn.close()

    # Statistiken berechnen
    total_termine = len(termine)
    heute_termine = len([t for t in termine if t['datum'] == str(heute)])
    zukunft_termine = len([t for t in termine if t['datum'] > str(heute)])

    return render_template('alle_termine.html',
                         termine=termine,
                         zeitraum=zeitraum,
                         sortierung=sortierung,
                         heute=heute,
                         stats={
                             'total': total_termine,
                             'heute': heute_termine,
                             'zukunft': zukunft_termine
                         })

@app.route('/meine_termine')
def meine_termine():
    """Zeigt IHRE persönlichen Termine"""
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
    print("🏥 CRM-Dashboard startet...")
    print("📅 Öffnen Sie http://localhost:5000 in Ihrem Browser")
    print("👤 Geben Sie Ihren Namen ein, um IHRE Termine zu sehen")
    app.run(debug=True, host='0.0.0.0', port=5000)
