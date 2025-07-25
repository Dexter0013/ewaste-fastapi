from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
from fastapi.responses import JSONResponse
import base64

app = FastAPI()

# Load your YOLO model (replace with your custom path if needed)
model = YOLO("best.pt")

# Allow requests from your frontend (adjust origin as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev use only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define your class names (update as per your model)
CLASS_NAMES = [
    "Battery","Cables","Keyboard","Laptop","monitor","mouse","pcb","phone"
]
# Define a color for each class (BGR format)
CLASS_COLORS = [
    (0,255,255),   # Battery - Yellow
    (0,255,0),     # Cables - Green
    (255,0,0),     # Keyboard - Blue
    (255,255,0),   # Laptop - Cyan
    (255,0,255),   # monitor - Magenta
    (0,0,255),     # mouse - Red
    (128,0,128),   # pcb - Purple
    (0,128,255)    # phone - Orange
]

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read and decode image
    img_bytes = await file.read()
    np_arr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Run YOLOv8 inference
    results = model(image)
    boxes = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        class_id = int(box.cls[0].cpu().numpy())
        conf = float(box.conf[0].cpu().numpy())
        class_name = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else str(class_id)
        color = CLASS_COLORS[class_id] if class_id < len(CLASS_COLORS) else (0,0,255)
        boxes.append({
            "x": int(x1),
            "y": int(y1),
            "width": int(x2 - x1),
            "height": int(y2 - y1),
            "class": str(class_id),
            "class_name": class_name,
            "confidence": conf
        })
        # Draw bounding box with class color
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(image, f"{class_name}:{conf:.2f}", (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Encode image to base64
    _, buffer = cv2.imencode('.jpg', image)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # Return image and boxes
    return JSONResponse(content={
        "image": img_base64,
        "boxes": boxes
    })