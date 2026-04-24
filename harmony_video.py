import streamlit as st
from gradio_client import Client
import tempfile
import os

# --------------------------------------
# CONFIG
# --------------------------------------
st.set_page_config(page_title="🎬 Pictator Video Engine", layout="wide")
st.title("🎬 AI Text → Video Generator (Stable Multi-Model)")

# --------------------------------------
# MODEL OPTIONS
# --------------------------------------
MODEL_OPTIONS = {
    "🔥 ModelScope 1.7B (Best)": "ali-vilab/text-to-video-ms-1.7b",
    "🎥 DAMO Original": "ali-vilab/modelscope-damo-text-to-video-synthesis",
    "⚡ Camenduru Fast": "camenduru/text-to-video-synthesis",
    "🧠 Diffusers T2V": "multimodalart/diffusers_text_to_video",
    "🚀 VDO Optimized": "vdo/text-to-video-ms-1.7b"
}

selected_label = st.selectbox("Choose Model", list(MODEL_OPTIONS.keys()))
MODEL_ID = MODEL_OPTIONS[selected_label]

# --------------------------------------
# INPUT
# --------------------------------------
prompt = st.text_area("Enter Prompt", height=150)
fps = st.slider("FPS", 8, 24, 12)
frames = st.slider("Frames (duration)", 8, 32, 16)

# --------------------------------------
# SAFE VIDEO EXTRACTION
# --------------------------------------
def extract_video(result):
    try:
        # Case 1: direct file path
        if isinstance(result, str) and os.path.exists(result):
            with open(result, "rb") as f:
                return f.read()

        # Case 2: tuple/list
        if isinstance(result, (list, tuple)):
            for item in result:
                if isinstance(item, str) and os.path.exists(item):
                    with open(item, "rb") as f:
                        return f.read()

        # Case 3: dict output
        if isinstance(result, dict):
            for v in result.values():
                if isinstance(v, str) and os.path.exists(v):
                    with open(v, "rb") as f:
                        return f.read()

        return None

    except Exception as e:
        st.error(f"Extraction error: {e}")
        return None

# --------------------------------------
# GENERATION FUNCTION (WITH FALLBACK)
# --------------------------------------
def generate_video(prompt, fps, frames):
    models_to_try = [
        MODEL_ID,
        "camenduru/text-to-video-synthesis",  # fallback
        "ali-vilab/text-to-video-ms-1.7b"
    ]

    for model in models_to_try:
        try:
            st.info(f"⚙️ Trying model: {model}")
            client = Client(model)

            try:
                result = client.predict(
                    prompt,
                    fps,
                    frames,
                    api_name="/predict"
                )
            except:
                # fallback signature (some models only take prompt)
                result = client.predict(prompt)

            video_bytes = extract_video(result)

            if video_bytes:
                return video_bytes

        except Exception as e:
            st.warning(f"⚠️ Failed on {model}: {e}")
            continue

    return None

# --------------------------------------
# GENERATE BUTTON
# --------------------------------------
if st.button("🎬 Generate Video"):

    if not prompt.strip():
        st.warning("Enter a prompt")
        st.stop()

    with st.spinner("Generating video (30–120 sec)..."):
        video_bytes = generate_video(prompt, fps, frames)

    if video_bytes:
        st.success("✅ Video generated successfully")
        st.video(video_bytes)

        st.download_button(
            "⬇️ Download Video",
            video_bytes,
            "output.mp4",
            "video/mp4"
        )
    else:
        st.error("❌ All models failed. Try shorter prompt or different model.")
