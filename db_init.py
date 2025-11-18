import sqlite3
import os

DATABASE_NAME = "leads.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            tag TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database {DATABASE_NAME} initialized successfully!")

def save_lead(name, phone, tag=None):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO leads (name, phone, tag)
        VALUES (?, ?, ?)
    ''', (name, phone, tag))
    
    conn.commit()
    lead_id = cursor.lastrowid
    conn.close()
    
    return lead_id

def get_all_leads():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
    leads = cursor.fetchall()
    
    conn.close()
    return leads

if __name__ == "__main__":
    init_db()
