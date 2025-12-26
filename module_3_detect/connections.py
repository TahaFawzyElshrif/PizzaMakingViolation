import mysql.connector
from kafka import KafkaConsumer,KafkaProducer
import json
from keys import *
import threading
import time
from collections import deque


#### Parameters
delay_frame = 6
buffer = 1


###### MYSQL DB

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="store_violations"
)

cursor = conn.cursor()



###### Kafka
consumer_to_simple_frames = KafkaConsumer(
    topic_camera_from_module1,
    bootstrap_servers=ip_wsl,
    fetch_max_bytes=10_000_000,        
    max_partition_fetch_bytes=10_000_000   
)

producer_to_violations = KafkaProducer(
    bootstrap_servers=ip_wsl+':9092',
    value_serializer=lambda v: json.dumps(v).encode(),
    max_request_size= 1399220
)



##### Kafka consumer filler queue

queue_frames = deque(maxlen = fps * delay_frame * buffer) 
stop_event_filling_queue = threading.Event()

def consumer_fill_queue(q, stop_event):
    i = 0

    consumer_to_simple_frames = KafkaConsumer(
    topic_camera_from_module1,
    bootstrap_servers=ip_wsl,
    fetch_max_bytes=10_000_000,        
    max_partition_fetch_bytes=10_000_000   
    )


    while not stop_event.is_set():
        
        
        msg = next(consumer_to_simple_frames)
        frame_data = json.loads(msg.value)
        
        
        #i += 1
    

        item = frame_data #i
        q.append(item)  
        
        #time.sleep(1/fps)
