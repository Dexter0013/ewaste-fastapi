from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
from fastapi.responses import JSONResponse
import base64
import tempfile
import os
from typing import List, Dict

app = FastAPI()

# Load your YOLO model
model = YOLO("Model\best.pt")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLASS_NAMES = ["Battery", "Cables", "Keyboard", "Laptop", "monitor", "mouse", "pcb", "phone"]
CLASS_COLORS = [
    (0, 255, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0),
    (255, 0, 255), (0, 0, 255), (128, 0, 128), (0, 128, 255)
]

def process_frame(frame: np.ndarray) -> Dict:
    """Process a single frame with YOLO model"""
    results = model(frame)
    boxes = []
    
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        class_id = int(box.cls[0].cpu().numpy())
        conf = float(box.conf[0].cpu().numpy())
        class_name = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else str(class_id)
        
        boxes.append({
            "x": int(x1),
            "y": int(y1),
            "width": int(x2 - x1),
            "height": int(y2 - y1),
            "class_name": class_name,
            "confidence": conf
        })
        
        # Draw bounding box
        color = CLASS_COLORS[class_id] if class_id < len(CLASS_COLORS) else (0, 0, 255)
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(frame, f"{class_name}:{conf:.2f}", (int(x1), int(y1)-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return {"frame": frame, "boxes": boxes}

def process_video(video_path: str) -> Dict:
    """Process video file and return annotated video with detections"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Use temporary file with proper codec
    output_path = os.path.join(tempfile.gettempdir(), "processed_output.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec for browser compatibility
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_results = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        processed = process_frame(frame)
        out.write(processed["frame"])
        frame_results.append({
            "frame_number": frame_count,
            "boxes": processed["boxes"]
        })
        frame_count += 1
    
    cap.release()
    out.release()
    
    # Read and encode video
    with open(output_path, "rb") as f:
        video_bytes = f.read()
    os.remove(output_path)
    
    return {
        "video": base64.b64encode(video_bytes).decode("utf-8"),
        "frames": frame_results,
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content_type = file.content_type
    
    if content_type.startswith("image/"):
        img_bytes = await file.read()
        np_arr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        processed = process_frame(image)
        _, buffer = cv2.imencode('.jpg', processed["frame"])
        
        return JSONResponse(content={
            "image": base64.b64encode(buffer).decode('utf-8'),
            "boxes": processed["boxes"],
            "type": "image"
        })
        
    elif content_type.startswith("video/"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        result = process_video(tmp_path)
        os.unlink(tmp_path)
        
        return JSONResponse(content={
            "video": result["video"],
            "frames": result["frames"],
            "fps": result["fps"],
            "frame_count": result["frame_count"],
            "width": result["width"],
            "height": result["height"],
            "type": "video"
        })
    
    return JSONResponse(
        status_code=400,
        content={"message": "Unsupported file type"}
    )