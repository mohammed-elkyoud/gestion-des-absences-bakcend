
from flask import Flask, request, jsonify
import numpy as np
import face_recognition
import cv2
import io
from PIL import Image

app = Flask(__name__)

# Exemple : embeddings déjà enregistrés (à remplacer par une base de données réelle)
# Charger des encodings depuis fichiers ou base de données
known_faces = {
    "etudiant1": np.load("embedding_etudiant1.npy"),
    "etudiant2": np.load("embedding_etudiant2.npy")
}

@app.route('/recognize', methods=['POST'])
def recognize_face():
    try:
        # Lire image envoyée en binaire
        image_stream = io.BytesIO(request.data)
        img = Image.open(image_stream).convert('RGB')
        img_array = np.array(img)

        # Détection et encodage des visages
        face_encodings = face_recognition.face_encodings(img_array)

        if not face_encodings:
            return jsonify({"status": "error", "message": "Aucun visage détecté"})

        input_encoding = face_encodings[0]

        for name, known_encoding in known_faces.items():
            matches = face_recognition.compare_faces([known_encoding], input_encoding, tolerance=0.5)
            if matches[0]:
                return jsonify({"status": "success", "identity": name})

        return jsonify({"status": "success", "identity": "inconnu"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
