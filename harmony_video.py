import streamlit as st
from gradio_client import Client
from PIL import Image
import os

# --------------------------------------
# CONFIG
# --------------------------------------
st.set_page_config(page_title="🎬 Pictator Video Engine", layout="wide")
st.title("🎬 AI Video Generator (Stable Hybrid Mode)")

# --------------------------------------
# MODE SELECTOR (IMPORTANT CHANGE)
# --------------------------------------
MODE = st.selectbox(
    "Choose Mode",
    ["🖼️ Image → Video (Recommended)", "🧪 Experimental Text → Video"]
)

# --------------------------------------
# INPUT
# --------------------------------------
prompt = st.text_area("Enter Prompt", height=150)

uploaded_image = st.file_uploader(
    "Upload Image (Recommended for best results)",
    type=["png", "jpg", "jpeg"]
)

input_image = None
if uploaded_image:
    input_image = Image.open(uploaded_image)
    st.image(input_image, caption="Input Image", use_container_width=True)

# --------------------------------------
# SAFE VIDEO EXTRACTION
# --------------------------------------
def extract_video(result):
    try:
        # Case 1: direct file path
        if isinstance(result, str) and os.path.exists(result):
            with open(result, "rb") as f:
                return f.read()

        # Case 2: list/tuple
        if isinstance(result, (list, tuple)):
            for item in result:
                if isinstance(item, str) and os.path.exists(item):
                    with open(item, "rb") as f:
                        return f.read()

        # Case 3: dict
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
# GENERATION ENGINE (FIXED)
# --------------------------------------
def generate_video(prompt, image=None):

    # ✅ 1. IMAGE → VIDEO (PRIMARY & WORKING)
    if MODE.startswith("🖼️") and image is not None:
        try:
            st.info("🎬 Using Stable Image → Video Model")
            client = Client("stabilityai/stable-video-diffusion-img2vid")

            result = client.predict(
                image,
                prompt,
                api_name="/predict"
            )

            video = extract_video(result)
            if video:
                return video

        except Exception as e:
            st.warning(f"Image→Video failed: {e}")

    # ⚠️ 2. TEXT → VIDEO (FALLBACK / EXPERIMENTAL)
    try:
        st.warning("⚠️ Using Experimental Text → Video")

        client = Client("cerspense/zeroscope_v2_XL")

        result = client.predict(prompt)

        video = extract_video(result)
        if video:
            return video

    except Exception as e:
        st.warning(f"Text→Video failed: {e}")

    return None

# --------------------------------------
# GENERATE BUTTON
# --------------------------------------
if st.button("🎬 Generate Video"):

    if not prompt.strip():
        st.warning("Enter prompt")
        st.stop()

    if MODE.startswith("🖼️") and input_image is None:
        st.warning("Upload an image for best results")
        st.stop()

    with st.spinner("Generating video (30–90 sec)..."):
        video_bytes = generate_video(prompt, input_image)

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
        st.error("❌ Generation failed (model limitations)")
