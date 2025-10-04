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



# Render UI


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
