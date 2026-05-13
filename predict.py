import tensorflow as tf
import cv2
import numpy as np

from mtcnn import MTCNN

# =====================================================
# LOAD MODEL
# =====================================================

model = tf.keras.models.load_model(
    "models/deepfake_model.h5"
)

detector = MTCNN()

IMG_SIZE = 299

# =====================================================
# SAFE FACE EXTRACTION
# =====================================================

def crop_face(img):

    try:

        faces = detector.detect_faces(img)

        if len(faces) == 0:
            return cv2.resize(img, (IMG_SIZE, IMG_SIZE))

        x, y, w, h = faces[0]['box']

        x = max(0, x)
        y = max(0, y)

        if w <= 0 or h <= 0:
            return cv2.resize(img, (IMG_SIZE, IMG_SIZE))

        face = img[y:y+h, x:x+w]

        if face.size == 0:
            return cv2.resize(img, (IMG_SIZE, IMG_SIZE))

        face = cv2.resize(face, (IMG_SIZE, IMG_SIZE))

        return face

    except:
        return cv2.resize(img, (IMG_SIZE, IMG_SIZE))

# =====================================================
# PREDICTION FUNCTION
# =====================================================

def predict_image(path):

    img = cv2.imread(path)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = crop_face(img)

    img = img.astype("float32") / 255.0

    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)[0][0]

    print("Prediction:", prediction)

    # LABELS:
    # fake = 0
    # real = 1

    if prediction >= 0.5:
        return "REAL", prediction
    else:
        return "FAKE", prediction