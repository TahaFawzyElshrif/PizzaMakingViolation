from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2
import time
import threading

app = FastAPI()

# List of videos to play
video_paths = [
    #"test_videos/test1.mp4",
    "test_videos/test2.mp4",
   #"test_videos/test3.mp4"
]

lock = threading.Lock()
current_index = 0
video = cv2.VideoCapture(video_paths[current_index])

def generate_frames():
    global video, current_index
    while True:
        with lock:
            success, frame = video.read()

            if not success:
                # Move to next video
                video.release()
                current_index = (current_index + 1) % len(video_paths)  # loop back
                video = cv2.VideoCapture(video_paths[current_index])
                time.sleep(0.05)
                continue

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(),
                             media_type='multipart/x-mixed-replace; boundary=frame')
