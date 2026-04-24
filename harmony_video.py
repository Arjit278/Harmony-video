import streamlit as st
import requests
import base64
import time

# --------------------------------------
# CONFIG
# --------------------------------------
st.set_page_config(page_title="🎬 Pictator Video Engine", layout="wide")
st.title("🎬 AI Video Generator (Fixed + Multi Model)")

# --------------------------------------
# MODEL OPTIONS (WORKING SPACES)
# --------------------------------------
MODEL_OPTIONS = {
    "🎥 Zeroscope XL": {
        "url": "https://huggingface-projects-zeroscope.hf.space",
        "type": "gradio"
    },
    "🎞️ Text2Video (ModelScope)": {
        "url": "https://damo-vilab-text-to-video.hf.space",
        "type": "gradio"
    }
}

selected_label = st.selectbox("Choose Model", list(MODEL_OPTIONS.keys()))
MODEL = MODEL_OPTIONS[selected_label]

# --------------------------------------
# INPUT
# --------------------------------------
prompt = st.text_area("Enter Prompt", height=150)

fps = st.slider("FPS", 8, 24, 12)
frames = st.slider("Frames", 8, 32, 16)

# --------------------------------------
# GRADIO API HANDLER (FIXED)
# --------------------------------------
def generate_video_gradio(prompt):
    try:
        base_url = MODEL["url"]

        # Step 1: Join queue
        join_url = f"{base_url}/queue/join"

        payload = {
            "data": [prompt, fps, frames],
            "fn_index": 0
        }

        r = requests.post(join_url, json=payload, timeout=60)

        if r.status_code != 200:
            st.error(f"Join failed: {r.status_code}")
            return None

        job = r.json()
        hash_id = job["hash"]

        # Step 2: Poll queue
        status_url = f"{base_url}/queue/data?hash={hash_id}"

        for _ in range(30):
            time.sleep(3)
            r2 = requests.get(status_url)

            if r2.status_code == 200:
                data = r2.json()

                if data["status"] == "COMPLETE":
                    video_path = data["data"][0]

                    # Download video
                    file_url = f"{base_url}/file={video_path}"
                    video_bytes = requests.get(file_url).content

                    return video_bytes

        st.error("⏳ Timeout waiting for video")
        return None

    except Exception as e:
        st.error(f"🔥 Error: {e}")
        return None

# --------------------------------------
# GENERATE
# --------------------------------------
if st.button("🎬 Generate Video"):

    if not prompt:
        st.warning("Enter prompt")
        st.stop()

    with st.spinner("Generating video (this may take 30-90 sec)..."):
        video_bytes = generate_video_gradio(prompt)

    if video_bytes:
        st.success("✅ Video generated")
        st.video(video_bytes)

        st.download_button(
            "⬇️ Download",
            video_bytes,
            "video.mp4",
            "video/mp4"
        )
    else:
        st.warning("⚠️ Generation failed")
