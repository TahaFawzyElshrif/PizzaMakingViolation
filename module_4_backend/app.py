from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2
import time
import threading
from contextlib import asynccontextmanager
import mysql.connector
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from keys import *
from utils import *

# ==============================
# Shared globals (IMPORTANT)
# ==============================
current_camera_frame = None
current_camera_viola = None

lock = threading.Lock()

# ==============================
# DB
# ==============================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="store_violations"
)

# ==============================
# Frame generator
# ==============================
def generate_frames(type_frame: str):
    global current_camera_frame,current_camera_viola
    while True:
        with lock:
            frame = (
                current_camera_frame
                if type_frame == "CAMERA"
                else current_camera_viola
            )

        if frame is None:
            time.sleep(0.01)
            continue

        print("frame received", flush=True)

        frame_img = get_image_from_base64(frame)
        ret, buffer = cv2.imencode(".jpg", frame_img)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )

current_camera_frame =  None
current_camera_viola =  None

def thread_camera_updator( stop_event,topic):
    global current_camera_frame

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=ip_wsl,
        fetch_max_bytes=10_000_000,        
        max_partition_fetch_bytes=10_000_000   
    ) # defination here to be thread safe
    
    while not stop_event.is_set():    
        msg = json.loads(next(consumer).value)
        current_camera_frame =  msg['frame_data']

            
        
        

def thread_viola_updator( stop_event,topic):
    global current_camera_viola

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=ip_wsl,
        fetch_max_bytes=10_000_000,        
        max_partition_fetch_bytes=10_000_000   
    ) # defination here to be thread safe
    
    while not stop_event.is_set():    
        msg = json.loads(next(consumer).value)
        current_camera_viola =  msg['frame_data']

       
# ==============================
# Lifespan (FIXED)
# ==============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global current_camera_frame
    print("LIFESPAN STARTED", flush=True)

    stop_thread_camera = threading.Event()
    stop_thread_viola = threading.Event()

    thread_camera = threading.Thread(
        target=thread_camera_updator,
        args=(stop_thread_camera, topic_camera),
        daemon=True,
    )
    thread_viola = threading.Thread(
        target=thread_viola_updator,
        args=(stop_thread_viola, topic_violaltion),
        daemon=True,
    )

    thread_camera.start()
    print("Camera thread started", flush=True)

    thread_viola.start()
    print("Violation tracker thread started", flush=True)
    current_camera_frame = "0000"
    generate_frames("CAMERA")
    # ✅ MUST yield — do NOT block here
    yield

    # ==============================
    # Shutdown
    # ==============================
    print("LIFESPAN SHUTDOWN", flush=True)
    stop_thread_camera.set()
    stop_thread_viola.set()

# ==============================
# FastAPI app
# ==============================
app = FastAPI(lifespan=lifespan)
# تفعيل CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يسمح لأي origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ==============================
# Routes
# ==============================
@app.get("/video/camera")
async def camera_feed():
    return StreamingResponse(
        generate_frames("CAMERA"),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

@app.get("/video/violation_camera")
async def violate_feed():
    return StreamingResponse(
        generate_frames("VIOLA"),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

@app.get("/api/items")
async def fetch_db():
    try:
        cursor = conn.cursor(dictionary=True)
        
        # استعلام على جدول العناصر
        cursor.execute("SELECT warned_frame_ingred, time_stamp_ingred, warned_frame_pizza FROM violations")
        rows = cursor.fetchall()

        # تجميع حسب التصنيف
        data = []
        for row in rows:
            
            data.append({
                "name": row["time_stamp_ingred"],
                "img": row["warned_frame_ingred"]
            })

        # تحويل لقائمة JSON متوافقة مع الـ frontend
        result = [{"title": "k", "elements": v} for  v in data]

        cursor.close()
        return JSONResponse(result)

    except Exception as e:
        print("DB fetch error:", e)
        return JSONResponse({"error": "Failed to fetch data"}, status_code=500)
