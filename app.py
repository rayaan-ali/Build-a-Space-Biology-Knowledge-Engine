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
st.set_page_config(page_title="Houston! We have a!", layout="wide")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    MODEL_NAME = "gemini-2.5-flash"
except Exception as e:
    st.error(f"Error configuring Gemini AI: {e}")
    st.stop()

# --- INITIALIZE SESSION STATE ---
if 'summary_dict' not in st.session_state:
    st.session_state.summary_dict = {}
    
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
    
    /* 🟢 FIX: Remove the hidden page link CSS to make the nav button visible */
    /* [data-testid="stPageLink"] { display: none; } */ 

    /* Push content to the top */
    .block-container { padding-top: 1rem !important; }
    
    /* Ensure no residual custom nav container is active */
    .nav-container { display: none; } 

    /* Main Theme */
    h1, h3 { text-align: center; }
    h1 { font-size: 4.5em !important; padding-bottom: 0.5rem; color: #000000; }
    h3 { color: #333333; }
    input[type="text"] {
        color: #000000 !important; background-color: #F0F2F6 !important;
        border: 1px solid #CCCCCC !important; border-radius: 8px; padding: 14px;
    }
    
    /* Result Card Styling (Full-Width) */
    .result-card {
        background-color: #FAFAFA; 
        padding: 1.5rem; 
        border-radius: 10px;
        margin-bottom: 1.5rem; /* More space between cards for UX */
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Title Styling */
    .result-card .stMarkdown strong { 
        font-size: 1.15em; 
        display: block;
        margin-bottom: 10px; 
    }

    /* Consistent Purple Link Color */
    a { color: #6A1B9A; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; }
    
    /* Summary Container (The inner block for summary text) */
    .summary-display {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px dashed #CCC;
    }
    
    /* BUTTON: Full-width button now replaced with auto-width for single column */
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
    
    /* Ensure Markdown headers in the summary are readable */
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

UI_STRINGS_EN = {
    "title": "Simplified Knowledge",
    "description": "A dynamic dashboard that summarizes NASA bioscience publications and explores impacts and results.",
    "upload_label": "Upload CSV data",
    "ask_label": "Ask anything:",
    "response_label": "Response:",
    "click_button": "Click here, nothing happens",
    "translate_dataset_checkbox": "Translate dataset column names (may take time)",
    "mention_label": "Official NASA Website",
    "button_response": "Hooray",
    "pdf_upload_header": "Upload PDFs to Summarize",
    "pdf_success": "✅ {count} PDF(s) uploaded and summarized",
    "pdf_summary_title": "📄 Summary: {name}",
    "search_label": "Search publications...",
    "results_header": "Found {count} matching publications:",
    "no_results": "No matching publications found.",
    "summarize_button": "🔬 Gather & Summarize"

}

# helpers
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
def extract_json_from_text(text: str):
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output.")
    return json.loads(text[start:end+1])

def translate_dict_via_gemini(source_dict: dict, target_lang_name: str):
    """
    Calls Gemini to translate the VALUES of a JSON object and returns a dict
    with the same keys and translated values. If Gemini fails, raises an exception
    which will be handled by the caller.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = (
            f"Translate the VALUES of the following JSON object into {target_lang_name}.\n"
            "Return ONLY a JSON object with the same keys and translated values (no commentary).\n"
            f"Input JSON:\n{json.dumps(source_dict, ensure_ascii=False)}\n"
        )
        resp = model.generate_content(prompt)
        return extract_json_from_text(resp.text)
    except Exception as e:
        # Reraise to be handled by outer logic so we can fallback gracefully.
        raise

def translate_list_via_gemini(items: list, target_lang_name: str):
    """
    Calls Gemini to translate a list of short strings and returns a list of translated strings.
    If Gemini fails, raises an exception for the caller to handle.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
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
    except Exception as e:
        # Reraise so caller can fallback
        raise

def perform_translation(lang_choice: str):
    """
    Centralized function to translate UI strings into 'lang_choice'.
    Shows emoji rain and spinner for ~6 seconds, attempts Gemini translation,
    and falls back to English if anything fails.
    """
    # If already the same language, just return current strings
    if lang_choice == st.session_state.current_lang and lang_choice in st.session_state.translations:
        st.session_state.translated_strings = st.session_state.translations[lang_choice]
        return st.session_state.translated_strings

    # visual animation and spinner (approx 6 seconds)
    rain(emoji="⏳", font_size=54, falling_speed=5, animation_length=2)
    with st.spinner(f"Translating UI to {lang_choice}..."):
        # ensure the spinner + animation last long enough
        start_t = time.time()
        try:
            if lang_choice in st.session_state.translations:
                translated_strings = st.session_state.translations[lang_choice]
            else:
                # Attempt to call Gemini to translate the known English UI strings
                translated_strings = translate_dict_via_gemini(st.session_state.translations["English"], lang_choice)
                st.session_state.translations[lang_choice] = translated_strings

            st.session_state.current_lang = lang_choice
            st.session_state.translated_strings = translated_strings
        except Exception as e:
            # If anything fails, fallback to English and show warning
            st.warning(f"Translation failed — using English. ({str(e)})")
            st.session_state.current_lang = "English"
            st.session_state.translated_strings = st.session_state.translations["English"]

        # Guarantee ~6 seconds total for UX (if translation was very fast)
        elapsed = time.time() - start_t
        if elapsed < 6:
            time.sleep(6 - elapsed)

    return st.session_state.translated_strings

# ----------------- TOP-RIGHT LANGUAGE SELECTOR (replaces earlier partial code) -----------------
_, col_language = st.columns([10, 1])
with col_language:
    st.markdown('<div class="language-dropdown-column">', unsafe_allow_html=True)
    # Show label text via LANGUAGES mapping
    # Use keys of LANGUAGES as options and format_func to show label
    try:
        index_default = list(LANGUAGES.keys()).index(st.session_state.current_lang)
    except ValueError:
        index_default = 0

    lang_choice = st.selectbox(
        "L",  # minimal label hidden via CSS
        options=list(LANGUAGES.keys()),
        index=index_default,
        format_func=lambda x: LANGUAGES[x]["label"] if isinstance(LANGUAGES.get(x), dict) else str(x),
        key="language_selector",
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Apply translation if needed (top selector)
perform_translation(lang_choice)
selected_language_code = LANGUAGES.get(st.session_state.current_lang, {}).get("code", "")

# Page
def search_page():
    # 🟢 FIX: Custom HTML Button for Assistant AI
    st.markdown(
        '<div class="nav-container-ai"><div class="nav-button-ai"><a href="/Assistant_AI" target="_self">Assistant AI 💬</a></div></div>',
        unsafe_allow_html=True
    )
        
    # --- UI Header ---
    df = load_data("SB_publication_PMC.csv")
    st.markdown('<h1>Houston! We Have A<span style="color: #6A1B9A;"> Problem!</span></h1>', unsafe_allow_html=True)
    st.markdown("### Search, Discover, and Summarize NASA's Bioscience Publications")

    search_query = st.text_input("Search publications...", placeholder="TELL US MORE!", label_visibility="collapsed")
    
    # --- Search Logic ---
    if search_query:
        mask = df["Title"].astype(str).str.contains(search_query, case=False, na=False)
        results_df = df[mask].reset_index(drop=True)
        st.markdown("---")
        st.subheader(f"Found {len(results_df)} matching publications:")
        
        if results_df.empty:
            st.warning("No matching publications found.")
        else:
            # Clear all session state summary variables to ensure clean display
            if 'summary_dict' not in st.session_state:
                 st.session_state.summary_dict = {}
            
            # SINGLE COLUMN DISPLAY LOOP (Stable)
            for idx, row in results_df.iterrows():
                summary_key = f"summary_{idx}"
                
                with st.container():
                    st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
                    
                    # Title
                    st.markdown(f"**Title:** <a href='{row['Link']}' target='_blank'>{row['Title']}</a>", unsafe_allow_html=True)
                    
                    # Button
                    if st.button("🔬 Gather & Summarize", key=f"btn_summarize_{idx}"):
                        
                        # GENERATE SUMMARY IMMEDIATELY UPON CLICK
                        with st.spinner(f"Accessing and summarizing: {row['Title']}..."):
                            try:
                                text = fetch_url_text(row['Link'])
                                summary = summarize_text_with_gemini(text)
                                st.session_state.summary_dict[summary_key] = summary
                            except Exception as e:
                                st.session_state.summary_dict[summary_key] = f"CRITICAL_ERROR: {e}"
                        
                        # Use rerun to ensure the display updates correctly across the whole page
                        st.rerun()

                    # DISPLAY SUMMARY IF IT EXISTS FOR THIS PUBLICATION
                    if summary_key in st.session_state.summary_dict:
                        summary_content = st.session_state.summary_dict[summary_key]
                        
                        st.markdown('<div class="summary-display">', unsafe_allow_html=True)
                        
                        if summary_content.startswith("ERROR") or summary_content.startswith("CRITICAL_ERROR"):
                            st.markdown(f"**❌ Failed to Summarize:** *{row['Title']}*", unsafe_allow_html=True)
                            st.error(f"Error fetching/summarizing content: {summary_content}")
                        else:
                            # Display the summary without an extra box, just the clean markdown
                            st.markdown(summary_content)
                            
                        st.markdown('</div>', unsafe_allow_html=True)
                            
                    st.markdown("</div>", unsafe_allow_html=True) 

if 'current_lang' not in st.session_state:
    st.session_state.current_lang = "English"  # Default language
if 'translations' not in st.session_state:
    st.session_state.translations = {"English": UI_STRINGS_EN.copy()}
if 'translated_strings' not in st.session_state:
    st.session_state.translated_strings = st.session_state.translations["English"]
    
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
#with st.sidebar:
  #  st.markdown("<h3 style='margin: 0; padding: 0;'>Upload PDFs to Summarize</h3>", unsafe_allow_html=True)
    #uploaded_files = st.file_uploader(label="", type=["pdf"], accept_multiple_files=True)

#if uploaded_files:
    #st.success(f"✅ {len(uploaded_files)} PDF(s) uploaded and summarized")
    #for uploaded_file in uploaded_files:
        #pdf_bytes = io.BytesIO(uploaded_file.read())
        #pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        #text = "".join([p.extract_text() or "" for p in pdf_reader.pages])
        #with st.spinner(f"Summarizing: {uploaded_file.name} ..."):
            #summary = summarize_text_with_gemini(text)
        #st.markdown(f"### 📄 Summary: {uploaded_file.name}")
        #st.write(summary)

# Translate dataset
#original_cols = list(df.columns)

# Deleted QUICK AI CHAT
# Replaced with page button, and sepearated
pg = st.navigation([
    st.Page(search_page, title="Simplified Knowledge 🔍"),
    st.Page("pages/Assistant_AI.py", title="Assistant AI 💬", icon="💬"),
])

pg.run()    
