import streamlit as st
import pandas as pd
import google.generativeai as genai

#SETUP / Config
st.set_page_config(page_title="Assistant AI", page_icon="💬", layout="wide")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    MODEL_NAME = "gemini-2.5-flash"
except Exception as e:
    st.error(f"Error configuring Gemini AI: {e}")
    st.stop()
