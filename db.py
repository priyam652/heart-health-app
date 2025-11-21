import sqlite3
from datetime import datetime
import csv

DB_NAME = "heart_data.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            bp INTEGER,
            chol INTEGER,
            max_hr INTEGER,
            ecg TEXT,
            risk TEXT,
            disease TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_prediction(name, age, bp, chol, max_hr, ecg, risk, disease):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (name, age, bp, chol, max_hr, ecg, risk, disease, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, bp, chol, max_hr, ecg, risk, disease, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def fetch_patient_history(name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT age, bp, chol, max_hr, ecg, risk, disease, timestamp
        FROM predictions
        WHERE name = ?
        ORDER BY timestamp DESC
    """, (name,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_all_predictions():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, age, bp, chol, max_hr, ecg, risk, disease, timestamp
        FROM predictions
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def export_patient_history_csv(name, filename="patient_history.csv"):
    rows = fetch_patient_history(name)
    headers = ["Age", "BP", "Chol", "Max HR", "ECG", "Risk", "Disease", "Timestamp"]
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return filename

def export_all_predictions_csv(filename="all_predictions.csv"):
    rows = fetch_all_predictions()
    headers = ["Name", "Age", "BP", "Chol", "Max HR", "ECG", "Risk", "Disease", "Timestamp"]
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return filename


