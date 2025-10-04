import streamlit as st
import google.generativeai as genai
import PyPDF2
import base64

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

st.title("📄 NASA Papers Summarizer")
st.write("Upload a NASA research paper to view it and get an AI summary side-by-side.")

# TO Upload PDF
uploaded_file = st.file_uploader("Upload a NASA PDF", type=["pdf"])

if uploaded_file is not None:
# THIS READS THE PDF
    pdf_bytes = uploaded_file.read()
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    
# TAKES OUT THE TEXT FROM THE PDF 
pdf_reader = PyPDF2.PdfReader(uploaded_file)
text = ""
for page in pdf_reader.pages:
    text += page.extract_text()

# Generates summaririze with ai  button
if st.button("🔍 Generate AI Summary"):
with st.spinner("Gemini is reading the paper..."):
response = model.generate_content(
f"Summarize this NASA research paper in under 300 words and include 3 key insights:\n\n{text}")
summary = response.text

# Display in 2 columns
col1, col2 = st.columns(2)
with col1:
st.subheader("Original Paper Uploads")
st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px"></iframe>', unsafe_allow_html=True)

with col2:
st.subheader("Gemini AI Summary")
st.write(summary)
