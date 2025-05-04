from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import os

app = Flask(__name__)

# Charger les embeddings
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
    app.run(debug=True)
