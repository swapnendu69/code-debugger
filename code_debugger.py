import base64
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

st.title("AI Code Debugger", anchor = False)
st.divider()

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
# Streamlit Cloud-এ .env থাকে না, তাই secrets থেকে নেবে
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

client = genai.Client(api_key = api_key)

uploaded_file = st.file_uploader("Upload your error screenshot", type = ["png", "jpg", "jpeg"])
if uploaded_file:
    st.image(uploaded_file, caption = "Uploaded screenshot")

option = st.radio(
    "What do you need?",
    ["Hints", "Solution with code"],
    index = None,
    horizontal = True,
)

PROMPTS = {
    "Hints": (
        "The image is a screenshot of a code error. "
        "Find the error or bug and give only step-by-step hints to fix it. "
        "Do not give the full corrected code. Format the answer in Markdown."
    ),
    "Solution with code": (
        "The image is a screenshot of a code error. "
        "Explain what the error is and why it happened, then give the full "
        "corrected code in a Markdown code block and briefly explain the fix."
    ),
}

if st.button("Debug Code", type = "primary"):
    if uploaded_file is None or option is None:
        st.error("Please upload an image and select Hints or Solution with code!")
    else:
        image_data = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
        with st.spinner("Debugging..."):
            interaction = client.interactions.create(
                model = "gemini-3.5-flash-lite",
                input = [
                    {"type": "text", "text": PROMPTS[option]},
                    {"type": "image", "data": image_data, "mime_type": uploaded_file.type},
                ],
            )
        st.divider()
        st.subheader(option)
        st.markdown(interaction.output_text)
