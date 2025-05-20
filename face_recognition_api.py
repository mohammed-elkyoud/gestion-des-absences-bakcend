from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import os
from db.database import init_db
from routes.professors import bp as profs_bp
from routes.classes import bp as classes_bp
from routes.students import bp as students_bp
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

init_db()

app.register_blueprint(profs_bp)
app.register_blueprint(classes_bp)
app.register_blueprint(students_bp)

# Charger les embedding
known_encodings = []
known_names = []

for file in os.listdir("embeddings"):
    if file.endswith(".npy"):
        name = file.replace(".npy", "")
        encoding = np.load(f"embeddings/{file}")
        known_encodings.append(encoding)
        known_names.append(name)

@app.route('/recognize_multiple', methods=['POST'])
def recognize_faces():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    image = face_recognition.load_image_file(image_file)
    unknown_encodings = face_recognition.face_encodings(image)

    if not unknown_encodings:
        return jsonify({'error': 'No faces found'}), 400

    recognized = []
    for encoding in unknown_encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding)
        if True in matches:
            index = matches.index(True)
            recognized.append(known_names[index])
        else:
            recognized.append("Unknown")

    return jsonify({'recognized_students': recognized})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
