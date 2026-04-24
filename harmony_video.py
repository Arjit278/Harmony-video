import streamlit as st
from gradio_client import Client
import os

st.set_page_config(page_title="🎬 Pictator Video Engine", layout="wide")
st.title("🎬 AI Video Generator (Working Version)")

# ✅ ONLY USE SPACES
MODEL_OPTIONS = {
    "🎥 ModelScope Official": "damo-vilab/text-to-video-ms",
    "⚡ Zeroscope Demo": "huggingface-projects/zeroscope",
    "🎞️ Text2Video Demo": "ali-vilab/text-to-video-ms-space"
}
selected_label = st.selectbox("Choose Model", list(MODEL_OPTIONS.keys()))
MODEL_ID = MODEL_OPTIONS[selected_label]

prompt = st.text_area("Enter Prompt", height=150)

# --------------------------------------
# SAFE EXTRACTION
# --------------------------------------
def extract_video(result):
    try:
        if isinstance(result, str) and os.path.exists(result):
            with open(result, "rb") as f:
                return f.read()

        if isinstance(result, (list, tuple)):
            for item in result:
                if isinstance(item, str) and os.path.exists(item):
                    with open(item, "rb") as f:
                        return f.read()

        return None
    except:
        return None

# --------------------------------------
# GENERATION
# --------------------------------------
def generate_video(prompt):
    models = list(MODEL_OPTIONS.values())

    for model in models:
        try:
            st.info(f"Trying: {model}")
            client = Client(model)

            try:
                result = client.predict(prompt, api_name="/predict")
            except:
                result = client.predict(prompt)

            video = extract_video(result)

            if video:
                return video

        except Exception as e:
            st.warning(f"{model} failed: {e}")

    return None

# --------------------------------------
# UI
# --------------------------------------
if st.button("🎬 Generate Video"):

    if not prompt.strip():
        st.warning("Enter prompt")
        st.stop()

    with st.spinner("Generating..."):
        video_bytes = generate_video(prompt)

    if video_bytes:
        st.success("✅ Done")
        st.video(video_bytes)

        st.download_button("Download", video_bytes, "video.mp4")
    else:
        st.error("❌ All Spaces failed (common issue)")
