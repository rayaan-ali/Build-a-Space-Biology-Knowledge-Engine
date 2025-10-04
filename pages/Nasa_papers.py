import streamlit as st
import google.generativeai as genai
import PyPDF2

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

st.title("NASA Research Papers")
st.write("Upload to view a NASSA paper and get a AI summary with it!")

uploaded_file = st.file_uploader("Upload a NASA PDF paper", type=["pdf"])

#TO DISPLAY PDF 
if uploaded_file is not None:
    st.download_button("📥 Download this paper", uploaded_file, file_name=uploaded_file.name)

    # THIS Extract text from PDF
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # THIS GENERATES summary
    if st.button("Summarize with Gemini 🚀"):
        with st.spinner("Summarizing..."):
            response = model.generate_content(
                f"Summarize this NASA research paper in under 300 words:\n\n{text}"
            )
            st.subheader("AI Summary")
            st.write(response.text)
