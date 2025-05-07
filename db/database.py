import sqlite3

def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS professors (
        id INTEGER PRIMARY KEY,
        firstName TEXT,
        lastName TEXT,
        matiere TEXT,
        gmailAcademique TEXT,
        classes TEXT,
        password TEXT,
        role TEXT DEFAULT 'professor'
    )''')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY,
        filiere TEXT,
        liste_des_etudiants TEXT
    )''')


    conn.commit()
    conn.close()
