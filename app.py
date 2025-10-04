import streamlit as st
import json
import io
import pandas as pd
import requests
from bs4 import BeautifulSoup
import PyPDF2
from functools import lru_cache
from streamlit_extras.let_it_rain import rain
from streamlit_extras.mention import mention

# ----------------- UI STRINGS -----------------
UI_STRINGS_EN = {
    "title": "Simplified Knowledge",
    "description": "A dynamic dashboard that summarizes NASA bioscience publications and explores impacts and results.",
    "upload_label": "Upload CSV data",
    "ask_label": "Ask anything:",
    "response_label": "Response:",
    "click_button": "Click here, nothing happens",
    "translate_dataset_checkbox": "Translate dataset column names (may take time)",
    "mention_label": "Official NASA Website",
    "button_response": "Hooray"
}

# ----------------- LANGUAGES -----------------
LANGUAGES = {
    "English": {"label": "🇺🇸 English (English)", "code": "en"},
    "Türkçe": {"label": "🇹🇷 Türkçe (Turkish)", "code": "tr"},
    "Français": {"label": "🇫🇷 Français (French)", "code": "fr"},
    "Español": {"label": "🇪🇸 Español (Spanish)", "code": "es"},
    # Add more languages as needed
}

# ----------------- Dummy Gemini translation -----------------
def translate_dict_via_gemini(source_dict, target_lang_name):
    # Dummy: just return the original dict
    return source_dict.copy()

def translate_list_via_gemini(items, target_lang_name):
    # Dummy: just return the original list
    return items.copy()

# ----------------- Streamlit session state -----------------
if "current_lang" not in st.session_state:
    st.session_state.current_lang = "English"
if "translations" not in st.session_state:
    st.session_state.translations = {"English": UI_STRINGS_EN.copy()}

# ----------------- Language selector -----------------
lang_choice = st.selectbox(
    "🌐 Language",
    options=list(LANGUAGES.keys()),
    format_func=lambda x: LANGUAGES[x]["label"],
    index=list(LANGUAGES.keys()).index(st.session_state.current_lang)
)

if lang_choice != st.session_state.current_lang:
    rain(emoji="⏳", font_size=54, falling_speed=5, animation_length=2)
    with st.spinner(f"Translating UI to {lang_choice}..."):
        try:
            if lang_choice in st.session_state.translations:
                translated_strings = st.session_state.translations[lang_choice]
            else:
                translated_strings = translate_dict_via_gemini(
                    st.session_state.translations["English"], lang_choice
                )
                st.session_state.translations[lang_choice] = translated_strings
            st.session_state.current_lang = lang_choice
        except Exception as e:
            st.error("Translation failed — using English. Error: " + str(e))
            translated_strings = st.session_state.translations["English"]
            st.session_state.current_lang = "English"
else:
    translated_strings = st.session_state.translations[st.session_state.current_lang]

# ----------------- UI Layout -----------------
st.set_page_config(page_title="NASA BioSpace Dashboard", layout="wide")
st.title(translated_strings["title"])
st.markdown(translated_strings["description"])

# ----------------- Load CSV -----------------
uploaded_csv = st.sidebar.file_uploader(
    translated_strings["upload_label"], type=["csv"]
)
if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    st.success(f"Loaded {len(df)} publications")
    st.dataframe(df.head())
    original_cols = df.columns.tolist()
else:
    st.info("Upload a CSV file to see publications")
    df = pd.DataFrame()
    original_cols = []

# ----------------- Translate dataset checkbox -----------------
translate_dataset = st.checkbox(translated_strings["translate_dataset_checkbox"])
if translate_dataset and original_cols:
    translated_cols = translate_list_via_gemini(original_cols, st.session_state.current_lang)
    df.rename(columns=dict(zip(original_cols, translated_cols)), inplace=True)

# ----------------- PDF Upload -----------------
uploaded_files = st.sidebar.file_uploader(
    "Upload one or more PDFs", type=["pdf"], accept_multiple_files=True
)
if uploaded_files:
    st.sidebar.success(f"✅ {len(uploaded_files)} PDF(s) uploaded")
    for uploaded_file in uploaded_files:
        pdf_bytes = io.BytesIO(uploaded_file.read())
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        st.write(f"Extracted {len(text)} chars from {uploaded_file.name}")
else:
    st.sidebar.info("Upload PDFs to extract text.")

# ----------------- Fetch URL text -----------------
@lru_cache(maxsize=256)
def fetch_url_text(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        r.raise_for_status()
    except Exception as e:
        return f"ERROR_FETCH: {str(e)}"
    content_type = r.headers.get("Content-Type", "").lower()
    if "pdf" in content_type or url.lower().endswith(".pdf"):
        try:
            pdf_bytes = io.BytesIO(r.content)
            reader = PyPDF2.PdfReader(pdf_bytes)
            text_parts = [p.extract_text() or "" for p in reader.pages]
            return "\n".join(text_parts)
        except Exception as e:
            return f"ERROR_PDF_PARSE: {str(e)}"
    else:
        try:
            soup = BeautifulSoup(r.text, "html.parser")
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
            return "\n\n".join(paragraphs)[:20000] if paragraphs else "ERROR_EXTRACT: No text found"
        except Exception as e:
            return f"ERROR_HTML_PARSE: {str(e)}"

# ----------------- Search publications -----------------
query = st.text_input("Enter keyword to search publications")
if query and not df.empty:
    results = df[df["Title"].astype(str).str.contains(query, case=False, na=False)]
    st.subheader(f"Results: {len(results)} matching titles")
else:
    results = pd.DataFrame(columns=df.columns)

# ----------------- Display results -----------------
for idx, row in results.iterrows():
    title = row["Title"]
    link = row.get("Link", "#")
    st.markdown(f"**[{title}]({link})**")

# Quick AI chat (uses small context sample)
st.markdown("---")
st.header("Chat with AI about the corpus (quick answers)")

q = st.text_input("Ask a question (answers will use the first ~2000 chars of the corpus):", key="chat_box")
if q:
    # Build a short context by concatenating first 200 abstracts/titles if available; here we only have titles/links so use top titles
    corpus_text = " ".join(df["Title"].astype(str).head(200).tolist())[:2000]
    prompt = f"Use the following corpus context (titles only):\n{corpus_text}\n\nQuestion: {q}\nAnswer concisely."
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(prompt)
        st.subheader("Answer:")
        st.write(resp.text)
    except Exception as e:
        st.error("AI chat failed: " + str(e))
