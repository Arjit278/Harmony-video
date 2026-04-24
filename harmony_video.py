import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

# --------------------------------------
# CONFIG
# --------------------------------------
st.set_page_config(page_title="🎬 Pictator Video Engine", layout="wide")
st.title("🎬 AI Video Generator (Cloud Ready)")

# --------------------------------------
# MODEL OPTIONS (SPACE BASED ✅)
# --------------------------------------
MODEL_OPTIONS = {
    "🎥 Zeroscope (Text→Video)": {
        "url": "https://cerspense-zeroscope-v2-xl.hf.space/run/predict",
        "type": "text"
    }
}

selected_label = st.selectbox("Choose Model", list(MODEL_OPTIONS.keys()))
MODEL = MODEL_OPTIONS[selected_label]

# --------------------------------------
# INPUT
# --------------------------------------
prompt = st.text_area("Enter Prompt", height=120)

uploaded_image = st.file_uploader("Upload Image (optional)", type=["png", "jpg", "jpeg"])

fps = st.slider("FPS", 8, 30, 16)
frames = st.slider("Frames (duration control)", 8, 48, 24)

# --------------------------------------
# VIDEO FUNCTION
# --------------------------------------
def generate_video_space(prompt, fps, frames):
    try:
        payload = {
            "data": [
                prompt,
                fps,
                frames
            ]
        }

        r = requests.post(MODEL["url"], json=payload, timeout=180)

        if r.status_code == 200:
            result = r.json()

            # HF Spaces returns base64 video
            video_b64 = result["data"][0]
            video_bytes = base64.b64decode(video_b64)

            return video_bytes

        else:
            st.error(f"❌ Error {r.status_code}: {r.text}")
            return None

    except Exception as e:
        st.error(f"🔥 Exception: {e}")
        return None

# --------------------------------------
# GENERATE
# --------------------------------------
if st.button("🎬 Generate Video"):

    if not prompt:
        st.warning("Enter a prompt")
        st.stop()

    with st.spinner("Generating video from HF Space..."):
        video_bytes = generate_video_space(prompt, fps, frames)

    if video_bytes:
        st.success("✅ Video generated")

        st.video(video_bytes)

        st.download_button(
            "⬇️ Download Video",
            video_bytes,
            "output.mp4",
            "video/mp4"
        )
    else:
        st.warning("⚠️ Generation failed")
