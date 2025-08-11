# Library imports
import numpy as np
import streamlit as st
import cv2
from keras.models import load_model
import tensorflow as tf

# Inject Custom CSS
st.markdown("""
    <style>
    :root {
        --primary-color: #7f6548;
        --secondary-color: #919a8a;
        --accent-color: #9c926a;
        --light-color: #343230;
        --dark-color: #935c29;
        --text-color: #2b1a0e;
        --border-radius: 8px;
        --box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
        --transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        --overlay-gradient: linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.2));
    }

    body {
        background-color: var(--light-color);
        color: var(--text-color);
        font-family: 'Segoe UI', sans-serif;
    }

    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border-radius: var(--border-radius);
        transition: var(--transition);
        box-shadow: var(--box-shadow);
    }

    .stButton>button:hover {
        background-color: var(--dark-color);
    }

    .stFileUploader {
        background-color: var(--secondary-color);
        border-radius: var(--border-radius);
        padding: 10px;
    }

    .stImage img {
        border: 4px solid var(--accent-color);
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
    }

    h1, .stTitle {
        color: var(--primary-color);
    }

    </style>
""", unsafe_allow_html=True)

# Load the Model
model = load_model('plant_disease_model.h5')

# Name of Classes
CLASS_NAMES = ('Tomato-Bacterial_spot', 'Potato-Barly blight', 'Corn-Common_rust')

# App UI
st.title("🌿 Plant Disease Detection")
st.markdown("Upload an image of the plant leaf to predict disease.")

plant_image = st.file_uploader("Choose an image...", type="jpg")
submit = st.button("Predict Disease")

# On Predict
if submit:
    if plant_image is not None:
        file_bytes = np.asarray(bytearray(plant_image.read()), dtype=np.uint8)
        opencv_image = cv2.imdecode(file_bytes, 1)

        st.image(opencv_image, channels="BGR", caption="Uploaded Leaf Image")
        st.write(f"Original Image Shape: {opencv_image.shape}")

        opencv_image = cv2.resize(opencv_image, (256, 256))
        opencv_image.shape = (1, 256, 256, 3)

        Y_pred = model.predict(opencv_image)
        result = CLASS_NAMES[np.argmax(Y_pred)]
        st.title(f"This is a {result.split('-')[0]} leaf with {result.split('-')[1]}")