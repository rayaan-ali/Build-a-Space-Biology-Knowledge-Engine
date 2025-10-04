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

#rain(emoji="⏳", font_size=54, falling_speed=5, animation_length="infinite")


st.title(" :gold[Simplified] :blue[Knowledge]")

st.write("A dynamic dashboard that summarizes a set of NASA bioscience publications and explore the impacts and results of experiments.")


uploaded_files = st.file_uploader("Upload CSV data", accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        st.write(df)

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
