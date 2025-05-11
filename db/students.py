import sqlite3

def get_db_connection():
    """Obtient une connexion à la base de données."""
    conn = sqlite3.connect('db/students.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Crée la table students si elle n'existe pas."""
    conn = get_db_connection()
    c = conn.cursor()

    # Crée la table pour stocker les informations des étudiants
    c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        image_path TEXT NOT NULL,
        classe TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

def insert_student(name, image_path, classe):
    """Insère un étudiant dans la base de données."""
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
    INSERT INTO students (name, image_path, classe)
    VALUES (?, ?, ?)
    ''', (name, image_path, classe))

    conn.commit()
    conn.close()

# Crée la base de données (table) si elle n'existe pas déjà
create_db()