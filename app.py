import streamlit as st
from ultralytics import YOLO
import numpy as np
from PIL import Image
import cv2
import tempfile
import av
from streamlit_webrtc import webrtc_streamer, RTCConfiguration

# --- PAGE CONFIG ---
st.set_page_config(page_title="E-Waste AI Dashboard", layout="wide", page_icon="♻️")

# --- DATABASE: Class-Specific Recommendations & Links ---
E_WASTE_INFO = {
    "Battery": {
        "impact": "CRITICAL: Fire & Toxic Risk",
        "rec": "Tape terminals to prevent short circuits. Never incinerate. Dispose only at specialty centers.",
        "link": "https://www.call2recycle.org/locator/",
        "label": "Call2Recycle Locator",
        "color": "#FF0000"
    },
    "Cables": {
        "impact": "Copper Recovery",
        "rec": "Bundle together. Copper is 100% recyclable and saves 85% energy vs mining.",
        "link": "https://recycleyourelectricals.org.uk/how-do-i-sort-out-my-cables/",
        "label": "Recycle Your Electricals",
        "color": "#808080"
    },
    "Keyboard": {
        "impact": "Plastic & Circuit Waste",
        "rec": "Remove batteries if wireless. Donate if functional; otherwise, drop at electronics retailers.",
        "link": "https://eridirect.com/sustainability/products-we-recycle/keyboards/",
        "label": "ERI Keyboard Recycling",
        "color": "#4B4B4B"
    },
    "Laptop": {
        "impact": "High: Precious Metals & Data",
        "rec": "Factory reset to wipe personal data. Take to manufacturer take-back programs (Dell/HP/Apple).",
        "link": "https://www.mi.com/in/support/terms/recycling_guide/",
        "label": "Xiaomi/Laptop Take-back",
        "color": "#0068C9"
    },
    "monitor": {
        "impact": "Toxic: Mercury & Lead",
        "rec": "Fragile: Do not crack the screen. Lead and mercury in the glass are environmental hazards.",
        "link": "https://www.samsung.com/in/microsite/care-for-clean-india/",
        "label": "Samsung Clean India Program",
        "color": "#FFD700"
    },
    "mouse": {
        "impact": "Small Electronic Waste",
        "rec": "Remove batteries. Recycle with other small peripherals at local drop-off bins.",
        "link": "https://www.logitech.com/en-in/sustainability/recycling.html",
        "label": "Logitech Global Recycling",
        "color": "#333333"
    },
    "pcb": {
        "impact": "Extreme: Gold & Silver Recovery",
        "rec": "Contains heavy metals (lead/cadmium). Must be processed by certified industrial recyclers.",
        "link": "https://www.twistedtraces.com/blog/a-comprehensive-guide-on-pcb-recycling-process-",
        "label": "PCB Recycling Guide",
        "color": "#8B4513"
    },
    "phone": {
        "impact": "Lithium & Rare Earths",
        "rec": "Remove SIM card. Take to retailer drop-boxes. Batteries are highly combustible.",
        "link": "https://www.motorola.in/legal/e-waste",
        "label": "Motorola/Mobile E-Waste",
        "color": "#29B09D"
    }
}

@st.cache_resource
def load_yolo():
    # Path to your Model/best.pt
    return YOLO("Model/best (3).pt")

model = load_yolo()

# --- SIDEBAR ---
st.sidebar.header("🛠️ Settings")
app_mode = st.sidebar.selectbox("Choose Input Mode", ["Image Upload", "Video Upload", "Live WebRTC Stream"])
conf_threshold = st.sidebar.slider("AI Confidence", 0.0, 1.0, 0.45)

st.title("♻️ Smart E-Waste Analytics Dashboard")

# --- HELPER FUNCTION FOR RESULTS ---
def display_recommendations(results):
    st.markdown("---")
    st.header("📋 Recycling Intelligence Report")
    
    # Extract unique detected classes
    detected_classes = list(set([model.names[int(box.cls)] for box in results[0].boxes]))
    
    if not detected_classes:
        st.info("No items identified in this view.")
        return

    cols = st.columns(len(detected_classes))
    for i, cls in enumerate(detected_classes):
        info = E_WASTE_INFO.get(cls, {
            "impact": "E-Waste", "rec": "Check local guidelines.", 
            "link": "https://www.epa.gov/recycle", "label": "EPA Guide", "color": "#FFFFFF"
        })
        
        with cols[i]:
            st.markdown(f"""
                <div style="background-color: #f1f3f6; padding:15px; border-radius:10px; border-top: 8px solid {info['color']}; min-height: 200px;">
                    <h3 style="color: black; margin-bottom: 5px;">{cls.capitalize()}</h3>
                    <p style="color: #d63031; font-weight: bold; font-size: 0.85em;">{info['impact']}</p>
                    <p style="color: #333; font-size: 0.9em;">{info['rec']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.link_button(f"Go to {info['label']}", info['link'], use_container_width=True)

# --- APP MODES ---
if app_mode == "Image Upload":
    file = st.file_uploader("Upload e-waste photo", type=['jpg', 'jpeg', 'png'])
    if file:
        img = Image.open(file)
        results = model.predict(np.array(img), conf=conf_threshold)
        
        c1, c2 = st.columns(2)
        c1.image(img, caption="Source", use_container_width=True)
        c2.image(results[0].plot(), caption="Detections", use_container_width=True)
        
        display_recommendations(results)

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
            results = model.predict(frame, conf=conf_threshold, verbose=False)
            st_frame.image(results[0].plot(), channels="BGR", use_container_width=True)
        vf.release()
        st.success("Video processed. For detailed links, use Image Mode on a screenshot.")

elif app_mode == "Live WebRTC Stream":
    st.subheader("🔴 Live AI Scanner")
    
    def video_frame_callback(frame):
        img = frame.to_ndarray(format="bgr24")
        results = model.predict(img, conf=conf_threshold, verbose=False)
        return av.VideoFrame.from_ndarray(results[0].plot(), format="bgr24")

    webrtc_streamer(
        key="ewaste-live",
        video_frame_callback=video_frame_callback,
        rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
        media_stream_constraints={"video": True, "audio": False},
    )
    
    st.divider()
    st.write("### Reference Recommendations")
    st.dataframe(E_WASTE_INFO, use_container_width=True)
