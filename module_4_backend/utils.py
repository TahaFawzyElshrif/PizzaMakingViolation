import cv2
import base64
import numpy as np
from kafka import KafkaConsumer,KafkaProducer
from keys import *
import json
import time

def get_image_from_base64(byte_encoded_img):
    # Decode base64 to bytes
    jpg_original = base64.b64decode(byte_encoded_img)

    # Convert bytes to numpy array
    nparr = np.frombuffer(jpg_original, np.uint8)

    # Decode image
    frame_recovered = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame_recovered

