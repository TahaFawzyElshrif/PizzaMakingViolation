from keys import *
import threading
import time
from kafka import KafkaConsumer,KafkaProducer
import json

stop_event_streamer = threading.Event()

print("Streamer module is started.")
def streamer( stop_event):

    consumer_to_simple_frames = KafkaConsumer(
        topic_camera_from_module1,
        bootstrap_servers=ip_wsl,
        fetch_max_bytes=10_000_000,        
        max_partition_fetch_bytes=10_000_000   
    ) # defination here to be thread safe
    producer = KafkaProducer(
        bootstrap_servers=ip_wsl+':9092',
        value_serializer=lambda v: json.dumps(v).encode(),
        max_request_size= 1399220
    ) # defination here to be thread safe

    iterator = 0
    while not stop_event.is_set():
         
        
        msg = json.loads(next(consumer_to_simple_frames).value)
        
        producer.send(topic_camera_consumer_yolo, (msg))
        producer.flush()

        producer.send(topic_camera_consumer_front , (msg))
        producer.flush()
        
    

        if (iterator%fps ==0):
            print("Frame "+str(iterator)+" sent")
            
        time.sleep(1/fps) # prevent flooding the broker
        iterator+=1
        

filler_thread = threading.Thread(target=streamer, args=(stop_event_streamer,), daemon=True)
filler_thread.start()

try:
    while True:
        time.sleep(1)  # keep main thread alive
except KeyboardInterrupt:
    stop_event_streamer.set()
    filler_thread.join()
