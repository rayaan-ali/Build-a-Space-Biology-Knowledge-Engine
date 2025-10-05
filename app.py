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
import streamlit as st
from streamlit_extras.mention import mention
import io
import google.generativeai as genai
MODEL_NAME = "gemini-2.5-flash"

# Gemini Ai
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    MODEL_NAME = "gemini-2.5-flash"
except Exception as e:
    st.error(f"Error configuring Gemini AI: {e}")
    st.stop()

# Load the CSV file with NASA publications
df = pd.read_csv("SB_publication_PMC.csv")  

# Everything with style / ux
st.markdown("""
    <style>
    /* Custom Nav button container for the top-left */
    .nav-container-ai {
        display: flex;
        justify-content: flex-start;
        padding-top: 3rem; 
        padding-bottom: 0rem;
    }
    .nav-button-ai a {
        background-color: #6A1B9A; /* Purple color */
        color: white; 
        padding: 10px 20px;
        border-radius: 8px; 
        text-decoration: none; 
        font-weight: bold;
        transition: background-color 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .nav-button-ai a:hover { 
        background-color: #4F0A7B; /* Darker purple on hover */
    }
    /* HIDE STREAMLIT'S DEFAULT NAVIGATION (Sidebar hamburger menu) */
    [data-testid="stSidebar"] { display: none; }
    
    /* [data-testid="stPageLink"] { display: none; } */ 

    .block-container { padding-top: 1rem !important; }
    
    .nav-container { display: none; } 

    #Main Theme 
    h1, h3 { text-align: center; }
    h1 { font-size: 4.5em !important; padding-bottom: 0.5rem; color: #000000; }
    h3 { color: #333333; }
    input[type="text"] {
        color: #000000 !important; background-color: #F0F2F6 !important;
        border: 1px solid #CCCCCC !important; border-radius: 8px; padding: 14px;
    }
        .result-card {
        background-color: #FAFAFA; 
        padding: 1.5rem; 
        border-radius: 10px;
        margin-bottom: 1.5rem; /* More space between cards for UX */
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    #Title Styling */
    .result-card .stMarkdown strong { 
        font-size: 1.15em; 
        display: block;
        margin-bottom: 10px; 
    }
    #Consistent Purple
    a { color: #6A1B9A; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; }
    
    #Summary Container (The inner block for summary text) */
    .summary-display {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px dashed #CCC;
    }
    
    #BUTTON: 
    .stButton>button {
        border-radius: 8px; 
        width: auto; /* Auto width based on content */
        min-width: 200px; 
        background-color: #E6E0FF;
        color: #4F2083; 
        border: 1px solid #C5B3FF; 
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover { background-color: #D6C9FF; border: 1px solid #B098FF; }
    
    #Markdown headers
    .summary-display h3 {
        text-align: left !important;
        color: #4F2083;
        margin-top: 15px;
        margin-bottom: 5px;
        font-size: 1.3em;
    }
    </style>
""", unsafe_allow_html=True)

# Languages
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

# UI strings, PLEASE KEEP UNCOMMENTED FOR NOW.
#UI_STRINGS_EN = {
   # "title": "Simplified Knowledge",
    #"description": "A dynamic dashboard that summarizes NASA bioscience publications and explores impacts and results.",
    #"ask_label": "Ask anything:",
    #"response_label": "Response:",
    #"about_us": "This dashboard explores NASA bioscience publications dynamically.",    
    #"translate_dataset_checkbox": "Translate dataset column names"
#}

# helper functions
@st.cache_data
def load_data(file_path): 
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}. Please ensure 'SB_publication_PMC.csv' is in the directory.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

@lru_cache(maxsize=128)
def fetch_url_text(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
    except requests.exceptions.RequestException as e: 
        return f"ERROR_FETCH: {e}"
    
    content_type = r.headers.get("Content-Type", "").lower()
    
    if "pdf" in content_type or url.lower().endswith(".pdf"):
        try:
            with io.BytesIO(r.content) as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
        except Exception as e: 
            return f"ERROR_PDF_PARSE: {e}"
    else:
        try:
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(['script', 'style']): tag.decompose()
            # Truncate content for Gemini model context limit
            return " ".join(soup.body.get_text(separator=" ", strip=True).split())[:25000]
        except Exception as e: 
            return f"ERROR_HTML_PARSE: {e}"

def summarize_text_with_gemini(text: str):
    if not text or text.startswith("ERROR"): 
        return f"Could not summarize due to a content error: {text.split(': ')[-1]}"

    prompt = (f"Summarize this NASA bioscience paper. Output in clean Markdown with a level 3 heading (###) titled 'Key Findings' (using bullet points) and a level 3 heading (###) titled 'Overview Summary' (using a paragraph).\n\nContent:\n{text}")
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: 
        return f"ERROR_GEMINI: {e}"
        
# Page
def search_page():
    st.markdown(
        '<div class="nav-container-ai"><div class="nav-button-ai"><a href="/Assistant_AI" target="_self">Assistant AI 💬</a></div></div>',
        unsafe_allow_html=True
    )
        
    # UI HEADER
    df = load_data("SB_publication_PMC.csv")
    st.markdown('<h1>Simplified <span style="color: #6A1B9A;">Knowledge</span></h1>', unsafe_allow_html=True)
    st.markdown("### Search, Discover, and Summarize NASA's Bioscience Publications")

    search_query = st.text_input("Search publications...", placeholder="e.g., microgravity, radiation, Artemis...", label_visibility="collapsed")

#Everything commented below is for backup just in case someething doesn't work DO NOT DELETE.
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

# THIS IS FOR UPLOADING PDF
with st.sidebar:
    st.markdown("<h3 style='margin: 0; padding: 0;'>Upload PDFs to Summarize</h3>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(label="", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} PDF(s) uploaded and summarized")
    for uploaded_file in uploaded_files:
        pdf_bytes = io.BytesIO(uploaded_file.read())
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        text = "".join([p.extract_text() or "" for p in pdf_reader.pages])
        with st.spinner(f"Summarizing: {uploaded_file.name} ..."):
            summary = summarize_text_with_gemini(text)
        st.markdown(f"### 📄 Summary: {uploaded_file.name}")
        st.write(summary)

#main ui
st.title(translated_strings["title"])
st.write(translated_strings["description"])

# Load CSV 
df = pd.read_csv("SB_publication_PMC.csv")

# Translate dataset
original_cols = list(df.columns)

if st.session_state.current_lang != "English":
    translated_cols = translate_list_via_gemini(original_cols, st.session_state.current_lang)
    df.rename(columns=dict(zip(original_cols, translated_cols)), inplace=True)

# Extract PDFs 
#if uploaded_pdfs:
    #st.success(f"{len(uploaded_pdfs)} PDF(s) uploaded")
    #for pdf_file in uploaded_pdfs:
        #pdf_bytes = io.BytesIO(pdf_file.read())
        #pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        #text = "".join([p.extract_text() or "" for p in pdf_reader.pages])
        #st.write(f"Extracted {len(text)} characters from {pdf_file.name}")

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

# SHOWS RESULTS 




# Deleted QUICK AI CHAT
# Replaced with page button, and sepearated
pg = st.navigation([
    st.Page(search_page, title="Simplified Knowledge 🔍"),
    st.Page("pages/Assistant_AI.py", title="Assistant AI 💬", icon="💬"),
])

pg.run()    
