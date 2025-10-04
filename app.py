import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import time
import altair as alt
from PIL import Image
import io
import json

uploaded_files = st.file_uploader("Upload CSV data", accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        st.write(df)
    
st.title("Simplified :blue[Knowledge] :sunglasses:")

st.write("Hello World")

















































# The End
