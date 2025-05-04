import sqlite3
import face_recognition
import numpy as np
import os

def generate_all_embeddings():
    conn = sqlite3.connect("db/students.db")
    c = conn.cursor()
    c.execute('SELECT name, image_path FROM students')
    students = c.fetchall()
    for name, image_path in students:
        if os.path.exists(image_path):
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                np.save(f"embeddings/{name}.npy", encodings[0])
                print(f"✅ Embedding créé pour {name}")
            else:
                print(f"⚠️ Aucun visage trouvé pour {name}")
        else:
            print(f"❌ Fichier manquant : {image_path}")
    conn.close()

generate_all_embeddings()
