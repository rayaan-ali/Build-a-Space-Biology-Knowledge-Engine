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


#rain(emoji="⏳", font_size=54, falling_speed=5, animation_length="infinite")

st.title(":red[Simplified]" ":blue[ Knowledge]")

##
#mention(
#label  = "Official NASA Website",
#icon  = "NASA International Space Apps Challenge",
#url = "https://www.spaceappschallenge.org/2025/local-events/mississauga/?tab=schedule"
#)
##


#st.logo("Profile Picture.jpg", size="large", link=None, icon_image=None)


st.logo("Profile Picture.jpg", size="large")

# Inject CSS to override header logo size
st.markdown(
    """
    <style>
    [data-testid="stHeader"] img {
        width: 500px !important;  /* change to your desired width */
        height: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write("A dynamic dashboard that summarizes a set of NASA bioscience publications and explore the impacts and results of experiments.")

uploaded_files = st.file_uploader("Upload CSV data", accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        st.write(df)
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

# BELOW CODE IS GEMINI CODE. Try not to use it as there's a free limit
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# USERINPUT.
user_input = st.text_input("Ask anything:", key="gemini_input")
if user_input:
    response = model.generate_content(user_input)
    st.subheader("Response:")
    st.write(response.text)




if st.button("Click here, nothing happens"):
    st.write("Hooray")














































# The End
