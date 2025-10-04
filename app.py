import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import time
import altair as alt
from PIL import Image
import io
import json
from streamlit_extras.let_it_rain import rain
from streamlit_extras.mention import mention
import PyPDF2
import base64
#rain(emoji="⏳", font_size=54, falling_speed=5, animation_length="infinite")

st.title(":red[Simplified]" ":blue[ Knowledge]")



left, middle, right = st.columns(3)
if left.button("Plain button", width="stretch"):
    left.markdown("You clicked the plain button.")
if middle.button("Emoji button", icon="😃", width="stretch"):
    middle.markdown("You clicked the emoji button.")
if right.button("Material button", icon=":material/mood:", width="stretch"):
    right.markdown("You clicked the Material button.")


# Setup Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# Language dropdown
language = st.selectbox("Select language:", ["English", "Turkish", "Spanish", "French"])

# Define your UI strings
ui_strings = {
    "title": "Simplified Knowledge",
    "description": "A dynamic dashboard that summarizes a set of NASA bioscience publications and explore the impacts and results of experiments.",
    "upload_label": "Upload CSV data",
    "ask_label": "Ask anything:"
}



#------------------------------------------------------------------------------------------#
# Emoji rain while translating
if language != "English":  # simulate translation only if not English
    rain(emoji="⏳", font_size=54, falling_speed=5, animation_length=2)  # runs for 2s
    time.sleep(2)  # simulate translation delay

    # Translate each UI string using Gemini
    translated_strings = {}
    for key, text in ui_strings.items():
        response = model.generate_content(f"Translate the following text to {language}:\n{text}")
        translated_strings[key] = response.text
else:
    translated_strings = ui_strings

# Render UI
st.title(translated_strings["title"])
st.write(translated_strings["description"])
uploaded_files = st.file_uploader(translated_strings["upload_label"], accept_multiple_files=True)
user_input = st.text_input(translated_strings["ask_label"], key="gemini_input")

#------------------------------------------------------------------------------------------#









st.write("A dynamic dashboard that summarizes a set of NASA bioscience publications and explore the impacts and results of experiments.")
#Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

st.title("NASA Papers Summarizer with Gemini Ai")
st.write("Upload a NASA research paper to view it and get an AI summary side-by-side.")

# THIS Uploads PDF
uploaded_file = st.file_uploader("Upload a NASA PDF", type=["pdf"])

if uploaded_file is not None:
    # Read PDF bytes 
    pdf_bytes = uploaded_file.read()
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    
    # Extract text with with libary pyPDF2
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # Generates summary with Gemini Api Keys
    if st.button("Generates AI Summary with Gemini Ai"):
        with st.spinner("Gemini is reading the paper..."):
            response = model.generate_content(
                f"Summarize this NASA research paper in under 300 words and include 3 key insights:\n\n{text}"
            )
            summary = response.text

        # Display in 2 columns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original Paper Uploaded")
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px"></iframe>',
                unsafe_allow_html=True
            )

        with col2:
            st.subheader("Gemini AI Summary")
            st.write(summary)

if st.button("Click here, nothing happens"):
    st.write("Hooray")














































# The End
