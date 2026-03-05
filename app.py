import streamlit as st
import cv2
import subprocess
from ultralytics import YOLO
import numpy as np
import tempfile
import os
import time
import av # Added for frame handling
from streamlit_webrtc import webrtc_streamer # Added for browser camera support

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Team Visionx 🤟", layout="wide")

if os.path.exists("Black.png"):
    st.image("Black.png", width=150)

st.title("🤟 Team Visionx")
st.markdown("### Smart Navigation & Object Detection using YOLO")

# ------------------ CONFIG ------------------
MODEL_PATH = "best.pt"

DANGER_CLASSES = ["knife", "scissors", "gun", "fire"]
MOVING_CLASSES = ["person", "car", "bus", "truck", "motorcycle", "bicycle"]

COOLDOWN_SECONDS = 3.0   # 🔥 SPEECH COOLDOWN

# ------------------ LOAD MODEL ------------------
@st.cache_resource
def load_model():
    model = YOLO(MODEL_PATH)
    return model

model = load_model()

# ------------------ SIDEBAR ------------------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["🤟 Detection", "⭐ Rate Us"])

st.sidebar.header("⚙️ Settings")
confidence = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
voice_enabled = st.sidebar.toggle("🔊 Enable Voice", value=True)

# ------------------ SPEECH ------------------
def speak_phrase(text):
    if voice_enabled and text:
        try:
            # -v en: English voice
            # -s 150: Speed (words per minute)
            subprocess.Popen(["espeak", "-v", "en", "-s", "150", text])
        except Exception as e:
            # This prevents the app from crashing if espeak isn't found
            st.error(f"Speech Error: {e}")

# ------------------ POSITION HELPER ------------------
def get_position(xmin, xmax, frame_width):
    cx = int((xmin + xmax) / 2)
    if cx < frame_width / 3:
        return "left"
    elif cx < 2 * frame_width / 3:
        return "center"
    else:
        return "right"

# ------------------ SMART NAVIGATION BRAIN ------------------
def smart_navigation(detections):
    if not detections:
        return "Path is clear. Move forward."

    enriched = []
    for cls, pos, area in detections:
        if cls in DANGER_CLASSES:
            pr = 1
        elif cls in MOVING_CLASSES:
            pr = 2
        else:
            pr = 3
        enriched.append((cls, pos, area, pr))

    enriched.sort(key=lambda x: (x[3], -x[2]))

    descriptions = []
    for cls, pos, area, pr in enriched[:3]:
        descriptions.append(f"{cls} on the {pos}")

    description_text = ". ".join(descriptions) + "."

    main_pos = enriched[0][1]

    if main_pos == "center":
        instruction = "Stop."
    elif main_pos == "left":
        instruction = "Move right."
    elif main_pos == "right":
        instruction = "Move left."
    else:
        instruction = "Move forward."

    return description_text + " " + instruction

# ------------------ SPEECH CONTROLLER ------------------
def should_speak(new_sentence):
    now = time.time()

    if "last_spoken_time" not in st.session_state:
        st.session_state.last_spoken_time = 0.0
        st.session_state.last_sentence = ""

    if new_sentence != st.session_state.last_sentence:
        st.session_state.last_spoken_time = now
        st.session_state.last_sentence = new_sentence
        return True

    if now - st.session_state.last_spoken_time >= COOLDOWN_SECONDS:
        st.session_state.last_spoken_time = now
        return True

    return False

# ------------------ DETECTION PAGE ------------------
if page == "🤟 Detection":
    st.header("🧭 Smart Navigation Assistant")
    mode = st.radio("Select Input Mode", ["📷 Webcam", "🖼️ Image", "🎞️ Video"])

    # ------------------ WEBCAM (ONLY PART CHANGED) ------------------
    if mode == "📷 Webcam":
        def video_frame_callback(frame):
            img = frame.to_ndarray(format="bgr24")
            img = cv2.flip(img, 1)
            h, w = img.shape[:2]

            results = model(img, conf=confidence, verbose=False)
            annotated = results[0].plot()

            detections = []
            for box in results[0].boxes:
                cls_id = int(box.cls)
                classname = model.names[cls_id]
                xmin, ymin, xmax, ymax = box.xyxy.cpu().numpy().squeeze().astype(int)
                position = get_position(xmin, xmax, w)
                area = (xmax - xmin) * (ymax - ymin)
                detections.append((classname, position, area))

            full_sentence = smart_navigation(detections)

            if should_speak(full_sentence):
                speak_phrase(full_sentence)

            return av.VideoFrame.from_ndarray(annotated, format="bgr24")

        webrtc_streamer(
            key="yolo-camera",
            video_frame_callback=video_frame_callback,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": True, "audio": False},
        )

    # ------------------ IMAGE (UNTOUCHED) ------------------
    elif mode == "🖼️ Image":
        uploaded = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
        if uploaded:
            file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)

            h, w = image.shape[:2]

            results = model(image, conf=confidence, verbose=False)
            annotated = results[0].plot()

            detections = []
            for box in results[0].boxes:
                cls_id = int(box.cls)
                classname = model.names[cls_id]
                xmin, ymin, xmax, ymax = box.xyxy.cpu().numpy().squeeze().astype(int)
                position = get_position(xmin, xmax, w)
                area = (xmax - xmin) * (ymax - ymin)
                detections.append((classname, position, area))

            full_sentence = smart_navigation(detections)

            st.image(annotated, channels="BGR")
            st.markdown(f"## 🧭 {full_sentence}")
            speak_phrase(full_sentence)

    # ------------------ VIDEO (UNTOUCHED) ------------------
    elif mode == "🎞️ Video":
        uploaded = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
        if uploaded:
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.write(uploaded.read())
            tmp.close()

            cap = cv2.VideoCapture(tmp.name)
            stframe = st.empty()
            nav_text = st.empty()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                h, w = frame.shape[:2]

                results = model(frame, conf=confidence, verbose=False)
                annotated = results[0].plot()

                detections = []
                for box in results[0].boxes:
                    cls_id = int(box.cls)
                    classname = model.names[cls_id]
                    xmin, ymin, xmax, ymax = box.xyxy.cpu().numpy().squeeze().astype(int)
                    position = get_position(xmin, xmax, w)
                    area = (xmax - xmin) * (ymax - ymin)
                    detections.append((classname, position, area))

                full_sentence = smart_navigation(detections)

                nav_text.markdown(f"## 🧭 {full_sentence}")

                if should_speak(full_sentence):
                    speak_phrase(full_sentence)

                stframe.image(annotated, channels="BGR")

            cap.release()
            os.unlink(tmp.name)

# ------------------ RATE US (UNTOUCHED) ------------------
elif page == "⭐ Rate Us":
    st.header("⭐ Rate Team VisionX")
    rating = st.slider("Rate us out of 5 ⭐", 1, 5, 5)
    feedback = st.text_area("Your feedback")
    if st.button("Submit"):
        st.success("Thank you for your feedback!")
        speak_phrase("Thank you for your feedback")

