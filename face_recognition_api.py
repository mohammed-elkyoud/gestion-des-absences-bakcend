from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import os

app = Flask(__name__)

# Charger tous les visages encodés
known_encodings = []
known_names = []

for file in os.listdir("embeddings"):
    if file.endswith(".npy"):
        name = file.replace(".npy", "")
        encoding = np.load(os.path.join("embeddings", file))
        known_encodings.append(encoding)
        known_names.append(name)

@app.route("/recognize", methods=["POST"])
def recognize():
    file = request.files["image"]
    image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(image)
    
    if not encodings:
        return jsonify({"error": "No face found"}), 400
    
    face_encoding = encodings[0]
    results = face_recognition.compare_faces(known_encodings, face_encoding)
    app.run(debug=True)
