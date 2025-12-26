import cv2
import base64
from keys import *
from utils import *
from kafka import KafkaProducer
import json
import time
from datetime import datetime



producer = KafkaProducer(
    bootstrap_servers=ip_wsl+':9092',
    value_serializer=lambda v: json.dumps(v).encode(),
    max_request_size= 1399220
)


camera = cv2.VideoCapture(camera_link)  
fps = camera.get(cv2.CAP_PROP_FPS)

print("Frame reader module is started.")

frame_id = 0
while True:
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame")
        break

    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    
    time_frame = time.time()
    producer.send(topic_camera, { "frame_data": jpg_as_text,"frame_id": frame_id,"timeDate": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))})
    producer.flush()
    frame_id += 1


    if (frame_id%fps ==0):
        print("Frame "+str(frame_id)+" sent")
        
    time.sleep(1/fps) # prevent flooding the broker
    