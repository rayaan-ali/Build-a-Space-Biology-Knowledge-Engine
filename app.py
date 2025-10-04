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
    "Arabic": {"label": "🇸🇦 العربية", "code": "ar"},
    "Bengali": {"label": "🇧🇩 বাংলা", "code": "bn"},
    "Bulgarian": {"label": "🇧🇬 Български", "code": "bg"},
    "Catalan": {"label": "🇪🇸 Català", "code": "ca"},
    "Chinese (Simplified)": {"label": "🇨🇳 中文 (简体)", "code": "zh"},
    "Chinese (Traditional)": {"label": "🇹🇼 中文 (繁體)", "code": "zh-TW"},
    "Croatian": {"label": "🇭🇷 Hrvatski", "code": "hr"},
    "Czech": {"label": "🇨🇿 Čeština", "code": "cs"},
    "Danish": {"label": "🇩🇰 Dansk", "code": "da"},
    "Dutch": {"label": "🇳🇱 Nederlands", "code": "nl"},
    "English": {"label": "🇺🇸 English", "code": "en"},
    "Estonian": {"label": "🇪🇪 Eesti", "code": "et"},
    "Filipino": {"label": "🇵🇭 Filipino", "code": "fil"},
    "Finnish": {"label": "🇫🇮 Suomi", "code": "fi"},
    "French": {"label": "🇫🇷 Français", "code": "fr"},
    "Georgian": {"label": "🇬🇪 ქართული", "code": "ka"},
    "German": {"label": "🇩🇪 Deutsch", "code": "de"},
    "Greek": {"label": "🇬🇷 Ελληνικά", "code": "el"},
    "Gujarati": {"label": "🇮🇳 ગુજરાતી", "code": "gu"},
    "Hebrew": {"label": "🇮🇱 עברית", "code": "he"},
    "Hindi": {"label": "🇮🇳 हिन्दी", "code": "hi"},
    "Hungarian": {"label": "🇭🇺 Magyar", "code": "hu"},
    "Icelandic": {"label": "🇮🇸 Íslenska", "code": "is"},
    "Indonesian": {"label": "🇮🇩 Bahasa Indonesia", "code": "id"},
    "Italian": {"label": "🇮🇹 Italiano", "code": "it"},
    "Japanese": {"label": "🇯🇵 日本語", "code": "ja"},
    "Kannada": {"label": "🇮🇳 ಕನ್ನಡ", "code": "kn"},
    "Korean": {"label": "🇰🇷 한국어", "code": "ko"},
    "Latvian": {"label": "🇱🇻 Latviešu", "code": "lv"},
    "Lithuanian": {"label": "🇱🇹 Lietuvių", "code": "lt"},
    "Macedonian": {"label": "🇲🇰 Македонски", "code": "mk"},
    "Malay": {"label": "🇲🇾 Bahasa Melayu", "code": "ms"},
    "Malayalam": {"label": "🇮🇳 മലയാളം", "code": "ml"},
    "Marathi": {"label": "🇮🇳 मराठी", "code": "mr"},
    "Mongolian": {"label": "🇲🇳 Монгол", "code": "mn"},
    "Norwegian": {"label": "🇳🇴 Norsk", "code": "no"},
    "Persian": {"label": "🇮🇷 فارسی", "code": "fa"},
    "Polish": {"label": "🇵🇱 Polski", "code": "pl"},
    "Portuguese": {"label": "🇵🇹 Português", "code": "pt"},
    "Punjabi": {"label": "🇮🇳 ਪੰਜਾਬੀ", "code": "pa"},
    "Romanian": {"label": "🇷🇴 Română", "code": "ro"},
    "Russian": {"label": "🇷🇺 Русский", "code": "ru"},
    "Serbian": {"label": "🇷🇸 Српски", "code": "sr"},
    "Slovak": {"label": "🇸🇰 Slovenčina", "code": "sk"},
    "Slovenian": {"label": "🇸🇮 Slovenščina", "code": "sl"},
    "Spanish": {"label": "🇪🇸 Español", "code": "es"},
    "Swahili": {"label": "🇰🇪 Kiswahili", "code": "sw"},
    "Swedish": {"label": "🇸🇪 Svenska", "code": "sv"},
    "Tamil": {"label": "🇮🇳 தமிழ்", "code": "ta"},
    "Telugu": {"label": "🇮🇳 తెలుగు", "code": "te"},
    "Thai": {"label": "🇹🇭 ไทย", "code": "th"},
    "Turkish": {"label": "🇹🇷 Türkçe", "code": "tr"},
    "Ukrainian": {"label": "🇺🇦 Українська", "code": "uk"},
    "Urdu": {"label": "🇵🇰 اردو", "code": "ur"},
    "Vietnamese": {"label": "🇻🇳 Tiếng Việt", "code": "vi"},
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
