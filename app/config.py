import os
import cv2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CONFIG = {
    'model_json_path': str(BASE_DIR / "ai_model" / "facialemotionmodel.json"),
    'model_weights_path': str(BASE_DIR / "ai_model" / "facialemotionmodel.h5"),
    'haar_cascade_path': cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
    'emotion_labels': {
        0: 'angry', 
        1: 'disgust', 
        2: 'fear', 
        3: 'happy', 
        4: 'neutral', 
        5: 'sad', 
        6: 'surprise'
    },
    'display_processing': False
}


GROQ_API_KEY = "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"

