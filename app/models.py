from keras.models import model_from_json
from config import CONFIG
import cv2


def load_emotion_model():
    """Load model"""
    with open(CONFIG['model_json_path'], "r") as json_file:
        model = model_from_json(json_file.read())
    model.load_weights(CONFIG['model_weights_path'])
    return model

def load_face_cascade():
    """Load Haar Cascade"""
    return cv2.CascadeClassifier(CONFIG['haar_cascade_path'])