import streamlit as st
import json
import time
import pandas as pd
import google.generativeai as genai
from streamlit_extras.let_it_rain import rain
from streamlit_extras.mention import mention

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

LANGUAGES = {
    "English": {"label": "🇺🇸 English", "code": "en"},
    "Türkçe": {"label": "🇹🇷 Türkçe", "code": "tr"},
    "Español": {"label": "🇪🇸 Español", "code": "es"},
    "Français": {"label": "🇫🇷 Français", "code": "fr"},
    "العربية": {"label": "🇸🇦 العربية", "code": "ar"},
    "中文": {"label": "🇨🇳 中文", "code": "zh"}
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
    "button_response": "Hooray"
}

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

if "current_lang" not in st.session_state:
    st.session_state.current_lang = "English"
if "translations" not in st.session_state:
    st.session_state.translations = {"English": UI_STRINGS_EN.copy()}

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

st.title(translated_strings["title"])
st.write(translated_strings["description"])

mention(
    label=translated_strings["mention_label"],
    icon="NASA International Space Apps Challenge",
    url="https://www.spaceappschallenge.org/"
)

uploaded_files = st.file_uploader(
    translated_strings["upload_label"], accept_multiple_files=True
)

translate_dataset = st.checkbox(translated_strings["translate_dataset_checkbox"])

if uploaded_files:
    for f in uploaded_files:
        df = pd.read_csv(f)
        original_cols = list(df.columns)

        if translate_dataset and lang_choice != "English":
            try:
                rain(emoji="💡", font_size=40, falling_speed=5, animation_length=2)
                with st.spinner("Translating column names..."):
                    translated_cols = translate_list_via_gemini(
                        original_cols, st.session_state.current_lang
                    )
                    col_map = dict(zip(original_cols, translated_cols))
                    df = df.rename(columns=col_map)
            except Exception as e:
                st.warning("Column translation failed: " + str(e))

        st.dataframe(df)

user_input = st.text_input(translated_strings["ask_label"], key="gemini_input")
if user_input:
    with st.spinner("Generating..."):
        resp = model.generate_content(user_input)
        st.subheader(translated_strings["response_label"])
        st.write(resp.text)

if st.button(translated_strings["click_button"]):
    st.write(translated_strings["button_response"])
