import face_recognition
import numpy as np
import sys
import os

image_path = sys.argv[1]
name = sys.argv[2]

image = face_recognition.load_image_file(image_path)
encoding = face_recognition.face_encodings(image)[0]

os.makedirs("embeddings", exist_ok=True)
np.save(f"embeddings/{name}.npy", encoding)
print(f"Embedding saved for {name}")
