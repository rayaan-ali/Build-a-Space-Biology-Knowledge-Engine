import streamlit as st
import json
import io
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import PyPDF2
from functools import lru_cache
from streamlit_extras.let_it_rain import rain
from streamlit_extras.mention import mention
import google.generativeai as genai
MODEL_NAME = "gemini-2.5-flash"

# ----------------- Configure Gemini API -----------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# Load the CSV file with NASA publications
df = pd.read_csv("SB_publication_PMC.csv")  # replace with your file path

# --- Custom CSS for white text in text boxes ---
st.markdown("""
    <style>
    /* Make all text inputs white */
    input[type="text"] {
        color: white !important;
    }
    /* Optional: darker background for the input box */
    input[type="text"] {
        background-color: #1e1e2f !important;
        border: 1px solid #444 !important;
    }
    /* Make placeholder text lighter so it's visible too */
    input::placeholder {
        color: #cccccc !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- Supported Languages -----------------
LANGUAGES = {
    "English": {"label": "English (English)", "code": "en"},
    "Türkçe": {"label": "Türkçe (Turkish)", "code": "tr"},
    "Français": {"label": "Français (French)", "code": "fr"},
    "Español": {"label": "Español (Spanish)", "code": "es"},
    "Afrikaans": {"label": "Afrikaans (Afrikaans)", "code": "af"},
    "العربية": {"label": "العربية (Arabic)", "code": "ar"},
    "Tiếng Việt": {"label": "Tiếng Việt (Vietnamese)", "code": "vi"},
    "isiXhosa": {"label": "isiXhosa (Xhosa)", "code": "xh"},
    "ייִדיש": {"label": "ייִדיש (Yiddish)", "code": "yi"},
    "Yorùbá": {"label": "Yorùbá (Yoruba)", "code": "yo"},
    "isiZulu": {"label": "isiZulu (Zulu)", "code": "zu"},
    "Deutsch": {"label": "Deutsch (German)", "code": "de"},
    "Italiano": {"label": "Italiano (Italian)", "code": "it"},
    "Русский": {"label": "Русский (Russian)", "code": "ru"},
    "日本語": {"label": "日本語 (Japanese)", "code": "ja"},
    "한국어": {"label": "한국어 (Korean)", "code": "ko"},
    "Polski": {"label": "Polski (Polish)", "code": "pl"},
    "Nederlands": {"label": "Nederlands (Dutch)", "code": "nl"},
    "Svenska": {"label": "Svenska (Swedish)", "code": "sv"},
    "Dansk": {"label": "Dansk (Danish)", "code": "da"},
    "Norsk": {"label": "Norsk (Norwegian)", "code": "no"},
    "Suomi": {"label": "Suomi (Finnish)", "code": "fi"},
    "हिन्दी": {"label": "हिन्दी (Hindi)", "code": "hi"},
    "বাংলা": {"label": "বাংলা (Bengali)", "code": "bn"},
    "ગુજરાતી": {"label": "ગુજરાતી (Gujarati)", "code": "gu"},
    "ಕನ್ನಡ": {"label": "ಕನ್ನಡ (Kannada)", "code": "kn"},
    "മലയാളം": {"label": "മലയാളം (Malayalam)", "code": "ml"},
    "मराठी": {"label": "मराठी (Marathi)", "code": "mr"},
    "ਪੰਜਾਬੀ": {"label": "ਪੰਜਾਬੀ (Punjabi)", "code": "pa"},
    "தமிழ்": {"label": "தமிழ் (Tamil)", "code": "ta"},
    "తెలుగు": {"label": "తెలుగు (Telugu)", "code": "te"},
    "Odia": {"label": "Odia (Odia)", "code": "or"},
    "עברית": {"label": "עברית (Hebrew)", "code": "he"},
    "فارسی": {"label": "فارسی (Persian)", "code": "fa"},
    "ไทย": {"label": "ไทย (Thai)", "code": "th"},
    "Bahasa Indonesia": {"label": "Bahasa Indonesia (Indonesian)", "code": "id"},
    "Malay": {"label": "Malay (Malay)", "code": "ms"},
    "Shqip": {"label": "Shqip (Albanian)", "code": "sq"},
    "Azərbaycan": {"label": "Azərbaycan (Azerbaijani)", "code": "az"},
    "Беларуская": {"label": "Беларуская (Belarusian)", "code": "be"},
    "Bosanski": {"label": "Bosanski (Bosnian)", "code": "bs"},
    "Български": {"label": "Български (Bulgarian)", "code": "bg"},
    "Hrvatski": {"label": "Hrvatski (Croatian)", "code": "hr"},
    "Čeština": {"label": "Čeština (Czech)", "code": "cs"},
    "Ελληνικά": {"label": "Ελληνικά (Greek)", "code": "el"},
    "Eesti": {"label": "Eesti (Estonian)", "code": "et"},
    "Latviešu": {"label": "Latviešu (Latvian)", "code": "lv"},
    "Lietuvių": {"label": "Lietuvių (Lithuanian)", "code": "lt"},
    "Magyar": {"label": "Magyar (Hungarian)", "code": "hu"},
    "Slovenčina": {"label": "Slovenčina (Slovak)", "code": "sk"},
    "Slovenščina": {"label": "Slovenščina (Slovenian)", "code": "sl"},
    "ქართული": {"label": "ქართული (Georgian)", "code": "ka"},
    "Հայերեն": {"label": "Հայերեն (Armenian)", "code": "hy"},
    "Қазақша": {"label": "Қазақша (Kazakh)", "code": "kk"},
    "Кыргызча": {"label": "Кыргызча (Kyrgyz)", "code": "ky"},
    "Монгол": {"label": "Монгол (Mongolian)", "code": "mn"},
    "Српски": {"label": "Српски (Serbian)", "code": "sr"},
    "Словенски": {"label": "Словенски (Slovene)", "code": "sl"},
    "தமிழ்": {"label": "தமிழ் (Tamil)", "code": "ta"},
    "ગુજરાતી": {"label": "ગુજરાતી (Gujarati)", "code": "gu"},
    "हिन्दी": {"label": "हिन्दी (Hindi)", "code": "hi"},
}


# ----------------- UI Strings -----------------
UI_STRINGS_EN = {
    "title": "Simplified Knowledge",
    "description": "A dynamic dashboard that summarizes NASA bioscience publications and explores impacts and results.",
    "ask_label": "Ask anything:",
    "response_label": "Response:",
    "translate_dataset_checkbox": "Translate dataset column names (may take time)",
    "mention_label": "Official NASA Website",
    "about_us": "This dashboard explores NASA bioscience publications dynamically."
}

# ----------------- Helper Functions -----------------
def extract_json_from_text(text):
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output.")
    return json.loads(text[start:end+1])

def translate_dict_via_gemini(source_dict: dict, target_lang_name: str):
    prompt = (
        f"Translate the VALUES of the following JSON object into {target_lang_name}.\n"
        "Return ONLY a JSON object with the same keys and translated values (no commentary).\n"
        f"Input JSON:\n{json.dumps(source_dict, ensure_ascii=False)}\n"
    )
    resp = model.generate_content(prompt)
    return extract_json_from_text(resp.text)

def translate_list_via_gemini(items: list, target_lang_name: str):
    prompt = (
        f"Translate this list of short strings into {target_lang_name}. "
        f"Return a JSON array of translated strings in the same order.\n"
        f"Input: {json.dumps(items, ensure_ascii=False)}\n"
    )
    resp = model.generate_content(prompt)
    start = resp.text.find('[')
    end = resp.text.rfind(']')
    if start == -1 or end == -1:
        raise ValueError("No JSON array found in model output.")
    return json.loads(resp.text[start:end+1])

@lru_cache(maxsize=256)
def fetch_url_text(url: str) -> str:
    """Download url and return extracted text (PDF or HTML). Cached in-memory."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; NASA-App/1.0)"}
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
    except Exception as e:
        return f"ERROR_FETCH: {str(e)}"

    content_type = r.headers.get("Content-Type", "").lower()
   
    # PDF
    if "pdf" in content_type or url.lower().endswith(".pdf"):
        try:
            pdf_bytes = io.BytesIO(r.content)
            reader = PyPDF2.PdfReader(pdf_bytes)
            text_parts = []
            for p in reader.pages:
                txt = p.extract_text()
                if txt:
                    text_parts.append(txt)
            return "\n".join(text_parts) if text_parts else "ERROR_EXTRACT: No text extracted from PDF, try again!"
        except Exception as e:
            return f"ERROR_PDF_PARSE: {str(e)}"
    # HTML
    else:
        try:
            soup = BeautifulSoup(r.text, "html.parser")
            # Extract visible paragraphs; ignore scripts/styles
            paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
            # Fallback: get text from body
            if not paragraphs:
                body = soup.body
                if body:
                    return body.get_text(separator=" ", strip=True)[:20000]
                return "ERROR_EXTRACT: No paragraph text found"
            return "\n\n".join(paragraphs)[:20000]  # limit to first 20k chars
        except Exception as e:
            return f"ERROR_HTML_PARSE: {str(e)}"

def summarize_text_with_gemini(text: str, max_output_chars: int = 1500) -> str:
    """Call Gemini to summarize text. Handles short texts and truncates long inputs."""
    if not text or text.startswith("ERROR"):
        return text
    # Keep prompt size reasonable: send first ~6000 chars of text
    context = text[:6000]
    prompt = (
        f"Summarize the following NASA bioscience paper content in clear bullet points and summary.\n\n"
        f"Content:\n{context}\n\nOutput: first give 3 short bullet points of key findings, then a 2-3 sentence plain summary."
    )
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"ERROR_GEMINI: {str(e)}"
    
# ----------------- Session State -----------------
if "current_lang" not in st.session_state:
    st.session_state.current_lang = "English"
if "translations" not in st.session_state:
    st.session_state.translations = {"English": UI_STRINGS_EN.copy()}

# ----------------- Page Config -----------------
# Page
st.set_page_config(page_title="NASA BioSpace Dashboard", layout="wide")
st.markdown(
    """
    <style>
    body { background-color: #0b3d91; color: white; }
    .stTextInput>div>div>input { color: black; }
    a { color: #00ffcc; }
    .result-card { background-color: #0e2a6b; padding: 12px; border-radius:8px; margin-bottom:10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------- Sidebar -----------------
with st.sidebar:
    # Language selection
    lang_choice = st.selectbox(
        "🌐 Choose language",
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
                        st.session_state.translations["English"],
                        lang_choice
                    )
                    st.session_state.translations[lang_choice] = translated_strings
                st.session_state.current_lang = lang_choice
            except Exception as e:
                st.error("Translation failed — using English. Error: " + str(e))
                translated_strings = st.session_state.translations["English"]
                st.session_state.current_lang = "English"
    else:
        translated_strings = st.session_state.translations[st.session_state.current_lang]


    # PDF upload
#st.sidebar.success(f"✅ {len(uploaded_files)} PDF(s) uploaded")
#for uploaded_file in uploaded_files:
        #pdf_bytes = io.BytesIO(uploaded_file.read())
        #pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        #text = ""
        #for page in pdf_reader.pages:
            #text += page.extract_text() or ""

    
        # Summarize each PDF
        #with st.spinner(f"Summarizing: {uploaded_file.name} ..."):
            #summary = summarize_text_with_gemini(text)
#else:
    #st.sidebar.info("Upload one or more PDF files to get summaries, try again!.")

# THIS IS FOR UPLOADIGN PDF
uploaded_files = st.sidebar.file_uploader(
    "Upload one or more PDFs", 
    type=["pdf"], 
    accept_multiple_files=True
)

#if uploaded_files:
st.sidebar.success(f"✅ {len(uploaded_files)} PDF(s) uploaded")
for uploaded_file in uploaded_files:
        pdf_bytes = io.BytesIO(uploaded_file.read())
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        # Summarize each PDF
        with st.spinner(f"Summarizing: {uploaded_file.name} ..."):
            summary = summarize_text_with_gemini(text)
else:
    st.sidebar.info("Upload one or more PDF files to get summaries, try again!.")

# ----------------- Main UI -----------------
st.title(translated_strings["title"])
st.write(translated_strings["description"])

mention(
    label=translated_strings["mention_label"],
    icon="NASA International Space Apps Challenge",
    url="https://www.spaceappschallenge.org/"
)

# ----------------- Load CSV -----------------
df = pd.read_csv("SB_publication_PMC.csv")

# ----------------- Translate dataset -----------------
translate_dataset = st.checkbox(translated_strings["translate_dataset_checkbox"])
if translate_dataset and original_cols and st.session_state.current_lang != "English":
    translated_cols = translate_list_via_gemini(original_cols, st.session_state.current_lang)
    df.rename(columns=dict(zip(original_cols, translated_cols)), inplace=True)

# ----------------- Extract PDFs -----------------
#if uploaded_pdfs:
    #st.success(f"{len(uploaded_pdfs)} PDF(s) uploaded")
    #for pdf_file in uploaded_pdfs:
        #pdf_bytes = io.BytesIO(pdf_file.read())
        #pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        #text = "".join([p.extract_text() or "" for p in pdf_reader.pages])
        #st.write(f"Extracted {len(text)} characters from {pdf_file.name}")

# ----------------- Search publications -----------------
# Center area - search box
search_col = st.container()
with search_col:
    query = st.text_input("Enter keyword to search publications (press Enter):", key="search_box")

if query:
    # Filter titles case-insensitively
    mask = df["Title"].astype(str).str.contains(query, case=False, na=False)
    results = df[mask].reset_index(drop=True)
    st.subheader(f"Results: {len(results)} matching titles")
    if len(results) == 0:
        st.info("No matching titles. Try broader keywords or search again!.")
else:
    results = pd.DataFrame(columns=df.columns) 

# SHOWS RESULTS (two-column layout for each result)
for idx, row in results.iterrows():
    title = row["Title"]
    link = row["Link"]
    st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
    st.markdown(f"**[{title}]({link})**")
    # Buttons: open link
    cols = st.columns([3,1,1])
    cols[0].write("")  # SPACER
    if cols[1].button("🔗 Open", key=f"open_{idx}"):
        st.markdown(f"[Open in new tab]({link})")
    if cols[2].button("Gather & Summarize", key=f"summ_{idx}"):
        with st.spinner("Gathering & extracting content..."):
            extracted = fetch_url_text(link)
        if extracted.startswith("ERROR"):
            st.error(extracted)
        else:
            st.success("Content has been succesfully accessed — calling Gemini for summary (this will take a few seconds)...")
            with st.spinner("Summarizing with Gemini Ai..."):
                summary = summarize_text_with_gemini(extracted)
            st.markdown("**AI Summary:**")
            st.write(summary)
    st.markdown("</div>", unsafe_allow_html=True)

# Quick AI chat (uses small context sample)
st.markdown("---")
st.header("Chat with AI for quick answers!")

q = st.text_input("Ask a question!", key="chat_box")

if q:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(q)  # <-- just send q directly
        st.subheader("Answer:")
        st.write(resp.text)
    except Exception as e:
        st.error("AI chat failed: " + str(e))
