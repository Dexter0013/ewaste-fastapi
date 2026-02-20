import streamlit as st
from ultralytics import YOLO
import numpy as np
from PIL import Image
import cv2
import tempfile
import av
from streamlit_webrtc import webrtc_streamer, RTCConfiguration

# --- PAGE CONFIG ---
st.set_page_config(page_title="E-Waste AI Analytics", layout="wide", page_icon="♻️")

# --- DATABASE: Specialized Recycling Info ---
E_WASTE_INFO = {
    "Battery": {"color": "red", "tip": "Toxic! Contains lithium. Take to hazardous waste centers only."},
    "Monitor": {"color": "blue", "tip": "Contains lead/mercury. Recycle via certified e-waste recyclers."},
    "Mobile": {"color": "green", "tip": "Valuable parts! Use manufacturer trade-in or specialty electronics bins."},
    "Keyboard": {"color": "gray", "tip": "Standard e-waste. Plastics and copper are recyclable."},
}

# --- MODEL LOADING ---
@st.cache_resource
def load_yolo():
    # Ensure your model is at this path in your repo
    return YOLO("Model/best.pt")

model = load_yolo()

# --- SIDEBAR ---
st.sidebar.title("🛠️ Control Panel")
app_mode = st.sidebar.selectbox("Select Input Mode", ["Image Upload", "Video Upload", "Live WebRTC Stream"])
conf_threshold = st.sidebar.slider("AI Confidence", 0.0, 1.0, 0.45)

# --- MAIN UI ---
st.title("♻️ Smart E-Waste Analytics Dashboard")

# 1. IMAGE MODE
if app_mode == "Image Upload":
    file = st.file_uploader("Upload e-waste photo", type=['jpg', 'jpeg', 'png'])
    if file:
        img = Image.open(file)
        results = model.predict(np.array(img), conf=conf_threshold)
        
        col1, col2 = st.columns(2)
        col1.image(img, caption="Original", use_container_width=True)
        col2.image(results[0].plot(), caption="AI Detection", use_container_width=True)
        
        # Specialized Class Output
        st.subheader("💡 Recycling Instructions")
        found_classes = [model.names[int(box.cls)] for box in results[0].boxes]
        if found_classes:
            for cls in set(found_classes):
                info = E_WASTE_INFO.get(cls, {"tip": "Check local disposal guidelines."})
                with st.expander(f"📍 {cls}"):
                    st.write(f"**Instructions:** {info['tip']}")
        else:
            st.info("No e-waste detected.")

# 2. VIDEO MODE
elif app_mode == "Video Upload":
    video_file = st.file_uploader("Upload e-waste video", type=['mp4', 'mov', 'avi'])
    if video_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        vf = cv2.VideoCapture(tfile.name)
        
        st_frame = st.empty()
        while vf.isOpened():
            ret, frame = vf.read()
            if not ret: break
            results = model.predict(frame, conf=conf_threshold, verbose=False)
            st_frame.image(results[0].plot(), channels="BGR", use_container_width=True)
        vf.release()

# 3. LIVE WEBRTC MODE
elif app_mode == "Live WebRTC Stream":
    st.subheader("🔴 Real-Time AI Inference")
    
    # Callback logic for frame processing
    def video_frame_callback(frame):
        img = frame.to_ndarray(format="bgr24")
        results = model.predict(img, conf=conf_threshold, verbose=False)
        annotated_img = results[0].plot()
        return av.VideoFrame.from_ndarray(annotated_img, format="bgr24")

    webrtc_streamer(
        key="ewaste-live",
        video_frame_callback=video_frame_callback,
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        ),
        media_stream_constraints={"video": True, "audio": False},
    )
    
    # Dashboard Info
    st.info("The live stream processes frames on the server. Latency depends on your connection.")
    st.sidebar.markdown("### How to use Live Mode")
    st.sidebar.write("1. Allow camera access\n2. Hold e-waste item to camera\n3. AI will detect instantly")
