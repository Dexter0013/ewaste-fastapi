import streamlit as st
from ultralytics import YOLO
import numpy as np
from PIL import Image
import cv2
import tempfile

# --- CONFIGURATION ---
st.set_page_config(page_title="E-Waste AI Dashboard", layout="wide")

# Specialized Recycling Info Database
E_WASTE_INFO = {
    "Battery": {"color": "red", "tip": "Contains lead/lithium. Do not throw in trash! Take to a specialized depot."},
    "Monitor": {"color": "blue", "tip": "Glass contains mercury. Handle with care and recycle via e-waste centers."},
    "Mobile": {"color": "green", "tip": "Contains precious metals like gold. Consider trade-in or refurbished programs."},
    "Keyboard": {"color": "gray", "tip": "Plastic components can be shredded and repurposed."},
}

@st.cache_resource
def load_model():
    return YOLO("Model/best.pt")

model = load_model()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Settings")
app_mode = st.sidebar.selectbox("Choose Input Mode", ["Image Upload", "Video Upload", "Live Webcam"])
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.4)

st.title("♻️ Smart E-Waste Analytics")

# --- MODE 1: IMAGE UPLOAD ---
if app_mode == "Image Upload":
    file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if file:
        img = Image.open(file)
        results = model.predict(np.array(img), conf=conf_threshold)
        
        col1, col2 = st.columns(2)
        col1.image(img, caption="Source", use_container_width=True)
        col2.image(results[0].plot(), caption="Detections", use_container_width=True)
        
        # Display specialized output
        st.subheader("Analysis & Recycling Guide")
        for box in results[0].boxes:
            label = model.names[int(box.cls)]
            info = E_WASTE_INFO.get(label, {"color": "white", "tip": "Check local e-waste guidelines."})
            with st.expander(f"📍 Detected: {label}"):
                st.write(f"**Action Plan:** {info['tip']}")

# --- MODE 2: VIDEO UPLOAD ---
elif app_mode == "Video Upload":
    video_file = st.file_uploader("Upload Video", type=['mp4', 'mov', 'avi'])
    if video_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        vf = cv2.VideoCapture(tfile.name)
        
        st_frame = st.empty()
        while vf.isOpened():
            ret, frame = vf.read()
            if not ret: break
            
            # Process frame
            results = model.predict(frame, conf=conf_threshold, verbose=False)
            res_plotted = results[0].plot()
            
            # Display frame-by-frame
            st_frame.image(res_plotted, channels="BGR", use_container_width=True)
        vf.release()

# --- MODE 3: LIVE WEBCAM ---
elif app_mode == "Live Webcam":
    img_file = st.camera_input("Take a snapshot for e-waste analysis")
    if img_file:
        img = Image.open(img_file)
        results = model.predict(np.array(img), conf=conf_threshold)
        st.image(results[0].plot(), use_container_width=True)
