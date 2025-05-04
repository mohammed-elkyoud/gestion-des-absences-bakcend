import sqlite3

def create_db():
    conn = sqlite3.connect('db/students.db')
    c = conn.cursor()

    # Crée la table pour stocker les informations des étudiants
    c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        image_path TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

def insert_student(name, image_path):
    conn = sqlite3.connect('db/students.db')
    c = conn.cursor()

    c.execute('''
    INSERT INTO students (name, image_path)
    VALUES (?, ?)
    ''', (name, image_path))

    conn.commit()
    conn.close()

# Crée la base de données et ajoute un étudiant d'exemple
create_db()


def show_students():
    conn = sqlite3.connect('db/students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    for row in c.fetchall():
        print(row)
    conn.close()


def delete_student_by_name(name):
    conn = sqlite3.connect('db/students.db')
    c = conn.cursor()

    # Vérifie si l'étudiant existe avant de supprimer
    c.execute("SELECT * FROM students WHERE name = ?", (name,))
    if c.fetchone() is not None:
        c.execute("DELETE FROM students WHERE name = ?", (name,))
        conn.commit()
        print(f"Étudiant {name} supprimé de la base de données.")
    else:
        print(f"L'étudiant {name} n'existe pas dans la base de données.")

    conn.close()


# Crée la base de données
create_db()

# Ajoute des étudiants
insert_student('cr7', 'known_faces/cr7.jpg')
insert_student('bale', 'known_faces/bale.jpg')
insert_student('benzima', 'known_faces/benzima.jpg')

# Affiche les étudiants dans la base
print("Liste des étudiants dans la base de données:")
show_students()

