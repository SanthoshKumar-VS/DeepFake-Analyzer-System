import os
import cv2
import numpy as np
import tensorflow as tf

from mtcnn import MTCNN

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import Xception
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

# =====================================================
# SETTINGS
# =====================================================

IMG_SIZE = 299
BATCH_SIZE = 8
EPOCHS = 15

TRAIN_DIR = "dataset/train"
TEST_DIR = "dataset/test"

# =====================================================
# FACE DETECTOR
# =====================================================

detector = MTCNN()

# =====================================================
# SAFE FACE EXTRACTION
# =====================================================

def crop_face(img):

    try:

        faces = detector.detect_faces(img)

        # No face found
        if len(faces) == 0:
            return cv2.resize(img, (IMG_SIZE, IMG_SIZE))

        x, y, w, h = faces[0]['box']

        # Safe coordinates
        x = max(0, x)
        y = max(0, y)

        # Invalid dimensions
        if w <= 0 or h <= 0:
            return cv2.resize(img, (IMG_SIZE, IMG_SIZE))

        face = img[y:y+h, x:x+w]

        # Empty crop protection
        if face.size == 0:
            return cv2.resize(img, (IMG_SIZE, IMG_SIZE))

        face = cv2.resize(face, (IMG_SIZE, IMG_SIZE))

        return face

    except:
        return cv2.resize(img, (IMG_SIZE, IMG_SIZE))

# =====================================================
# PREPROCESS FUNCTION
# =====================================================

def preprocess_image(img):

    img = img.astype("uint8")

    img = crop_face(img)

    img = img.astype("float32") / 255.0

    return img

# =====================================================
# DATA GENERATORS
# =====================================================

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_image,
    rotation_range=15,
    zoom_range=0.15,
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_image
)

# =====================================================
# LOAD DATA
# =====================================================

train_data = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary'
)

test_data = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary'
)

print(train_data.class_indices)

# =====================================================
# LOAD XCEPTION MODEL
# =====================================================

base_model = Xception(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

# Fine tuning enabled
base_model.trainable = True

# Freeze first layers
for layer in base_model.layers[:80]:
    layer.trainable = False

# =====================================================
# CUSTOM CLASSIFIER
# =====================================================

x = base_model.output

x = GlobalAveragePooling2D()(x)

x = Dropout(0.5)(x)

x = Dense(512, activation='relu')(x)

x = Dropout(0.3)(x)

x = Dense(256, activation='relu')(x)

prediction = Dense(1, activation='sigmoid')(x)

model = Model(
    inputs=base_model.input,
    outputs=prediction
)

# =====================================================
# COMPILE MODEL
# =====================================================

model.compile(
    optimizer=Adam(learning_rate=0.00001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# =====================================================
# TRAIN MODEL
# =====================================================

history = model.fit(
    train_data,
    validation_data=test_data,
    epochs=EPOCHS
)

# =====================================================
# SAVE MODEL
# =====================================================

model.save("models/deepfake_model.h5")

print("FINAL MODEL TRAINED SUCCESSFULLY")