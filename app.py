import streamlit as st
from ultralytics import YOLO
import numpy as np
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(page_title="E-Waste AI Detector", layout="wide")

# --- STEP 1: MODEL LOADING (The "Brain") ---
# Use @st.cache_resource so the model stays in memory across different users
@st.cache_resource
def load_yolo_model():
    # Update 'best.pt' to the path of your trained weights file
    model = YOLO("Models/best.pt") 
    return model

try:
    model = load_yolo_model()
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# --- STEP 2: USER INTERFACE ---
st.title("♻️ E-Waste Classification System")
st.write("Upload a photo of electronic devices to identify and classify them for recycling.")

uploaded_file = st.file_uploader("Upload an image (JPG, PNG, JPEG)", type=['jpg', 'jpeg', 'png'])

# --- STEP 3: INFERENCE LOGIC ---
if uploaded_file is not None:
    # Read the image
    image = Image.open(uploaded_file)
    
    # Create two columns for a side-by-side view
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        st.image(image, use_container_width=True)
    
    with st.spinner("Detecting E-Waste..."):
        # Convert PIL image to numpy for YOLO
        img_array = np.array(image)
        
        # Run Detection
        results = model.predict(img_array, conf=0.4) # Adjust confidence threshold as needed
        
        # Get annotated image (plotted with boxes/labels)
        annotated_frame = results[0].plot()
        
    with col2:
        st.subheader("AI Detection Result")
        st.image(annotated_frame, channels="RGB", use_container_width=True)

    # --- STEP 4: RESULT SUMMARY ---
    st.divider()
    st.subheader("📋 Detection Inventory")
    
    # Extract data for a clean table
    detections = results[0].boxes
    if len(detections) > 0:
        counts = {}
        for box in detections:
            label = model.names[int(box.cls)]
            counts[label] = counts.get(label, 0) + 1
        
        # Display as metrics
        cols = st.columns(len(counts))
        for i, (item, count) in enumerate(counts.items()):
            cols[i].metric(label=item, value=count)
    else:
        st.info("No e-waste items detected in this image.")
