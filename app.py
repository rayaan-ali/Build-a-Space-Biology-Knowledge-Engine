import streamlit as st
import json
import time
import pandas as pd
import google.generativeai as genai 
from streamlit_extras.let_it_rain import rain
from streamlit_extras.mention import mention
import requests
from bs4 import BeautifulSoup
import io
import PyPDF2
from urllib.parse import urlparse
from functools import lru_cache

# UI layout
st.title("Simplfied Knowledge")
st.markdown("Search the catalog and fetch & summarize linked pages (PDF or HTML).")

# Load the CSV file with NASA publications
df = pd.read_csv("SB_publication_PMC.csv")  # replace with your file path

# UI layout
st.title("Simplfied Knowledge")
st.markdown("Search the catalog and fetch & summarize linked pages (PDF or HTML).")

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

#EVERYTHING BELOW LANGAUGES
LANGUAGES = {
"Afrikaans": {"label": "🇿🇦 Afrikaans", "code": "af"},
"العربية": {"label": "🇸🇦 العربية", "code": "ar"},
"Հայերեն": {"label": "🇦🇲 Հայերեն", "code": "hy"},
"Azərbaycan dili": {"label": "🇦🇿 Azərbaycan dili", "code": "az"},
"Euskara": {"label": "🇪🇸 Euskara", "code": "eu"},
"Беларуская": {"label": "🇧🇾 Беларуская", "code": "be"},
"বাংলা": {"label": "🇧🇩 বাংলা", "code": "bn"},
"Bosanski": {"label": "🇧🇦 Bosanski", "code": "bs"},
"Български": {"label": "🇧🇬 Български", "code": "bg"},
"Català": {"label": "🇪🇸 Català", "code": "ca"},
"中文": {"label": "🇨🇳 中文", "code": "zh"},
"Hrvatski": {"label": "🇭🇷 Hrvatski", "code": "hr"},
"Čeština": {"label": "🇨🇿 Čeština", "code": "cs"},
"Dansk": {"label": "🇩🇰 Dansk", "code": "da"},
"Nederlands": {"label": "🇳🇱 Nederlands", "code": "nl"},
"English": {"label": "🇺🇸 English", "code": "en"},
"Esperanto": {"label": "🌍 Esperanto", "code": "eo"},
"Eesti": {"label": "🇪🇪 Eesti", "code": "et"},
"Suomi": {"label": "🇫🇮 Suomi", "code": "fi"},
"Français": {"label": "🇫🇷 Français", "code": "fr"},
"Galego": {"label": "🇪🇸 Galego", "code": "gl"},
"ქართული": {"label": "🇬🇪 ქართული", "code": "ka"},
"Deutsch": {"label": "🇩🇪 Deutsch", "code": "de"},
"Ελληνικά": {"label": "🇬🇷 Ελληνικά", "code": "el"},
"ગુજરાતી": {"label": "🇮🇳 ગુજરાતી", "code": "gu"},
"Hausa": {"label": "🇳🇬 Hausa", "code": "ha"},
"עברית": {"label": "🇮🇱 עברית", "code": "he"},
"हिन्दी": {"label": "🇮🇳 हिन्दी", "code": "hi"},
"Magyar": {"label": "🇭🇺 Magyar", "code": "hu"},
"Íslenska": {"label": "🇮🇸 Íslenska", "code": "is"},
"Bahasa Indonesia": {"label": "🇮🇩 Bahasa Indonesia", "code": "id"},
"Gaeilge": {"label": "🇮🇪 Gaeilge", "code": "ga"},
"Italiano": {"label": "🇮🇹 Italiano", "code": "it"},
"日本語": {"label": "🇯🇵 日本語", "code": "ja"},
"Basa Jawa": {"label": "🇮🇩 Basa Jawa", "code": "jv"},
"ಕನ್ನಡ": {"label": "🇮🇳 ಕನ್ನಡ", "code": "kn"},
"Қазақ тілі": {"label": "🇰🇿 Қазақ тілі", "code": "kk"},
"ភាសាខ្មែរ": {"label": "🇰🇭 ភាសាខ្មែរ", "code": "km"},
"한국어": {"label": "🇰🇷 한국어", "code": "ko"},
"Kurdî": {"label": "🇹🇯 Kurdî", "code": "ku"},
"Кыргызча": {"label": "🇰🇬 Кыргызча", "code": "ky"},
"ລາວ": {"label": "🇱🇦 ລາວ", "code": "lo"},
"Latviešu": {"label": "🇱🇻 Latviešu", "code": "lv"},
"Lietuvių": {"label": "🇱🇹 Lietuvių", "code": "lt"},
"Македонски": {"label": "🇲🇰 Македонски", "code": "mk"},
"Malagasy": {"label": "🇲🇬 Malagasy", "code": "mg"},
"Bahasa Melayu": {"label": "🇲🇾 Bahasa Melayu", "code": "ms"},
"Malti": {"label": "🇲🇹 Malti", "code": "mt"},
"Монгол": {"label": "🇲🇳 Монгол", "code": "mn"},
"नेपाली": {"label": "🇳🇵 नेपाली", "code": "ne"},
"Norsk": {"label": "🇳🇴 Norsk", "code": "no"},
"پښتو": {"label": "🇦🇫 پښتو", "code": "ps"},
"فارسی": {"label": "🇮🇷 فارسی", "code": "fa"},
"Polski": {"label": "🇵🇱 Polski", "code": "pl"},
"Português": {"label": "🇵🇹 Português", "code": "pt"},
"ਪੰਜਾਬੀ": {"label": "🇮🇳 ਪੰਜਾਬੀ", "code": "pa"},
"Română": {"label": "🇷🇴 Română", "code": "ro"},
"Русский": {"label": "🇷🇺 Русский", "code": "ru"},
"Српски": {"label": "🇷🇸 Српски", "code": "sr"},
"Svenska": {"label": "🇸🇪 Svenska", "code": "sv"},
"Kiswahili": {"label": "🇹🇿 Kiswahili", "code": "sw"},
"தமிழ்": {"label": "🇮🇳 தமிழ்", "code": "ta"},
"తెలుగు": {"label": "🇮🇳 తెలుగు", "code": "te"},
"ไทย": {"label": "🇹🇭 ไทย", "code": "th"},
"Türkçe": {"label": "🇹🇷 Türkçe", "code": "tr"},
"Українська": {"label": "🇺🇦 Українська", "code": "uk"},
"اردو": {"label": "🇵🇰 اردو", "code": "ur"},
"O‘zbek": {"label": "🇺🇿 O‘zbek", "code": "uz"},
"Tiếng Việt": {"label": "🇻🇳 Tiếng Việt", "code": "vi"},
"isiXhosa": {"label": "🇿🇦 isiXhosa", "code": "xh"},
"ייִדיש": {"label": "🇮🇱 ייִדיש", "code": "yi"},
"Yorùbá": {"label": "🇳🇬 Yorùbá", "code": "yo"},
"isiZulu": {"label": "🇿🇦 isiZulu", "code": "zu"},
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

translate_dataset = st.checkbox(translated_strings["translate_dataset_checkbox"])

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
st.write(translated_strings["button_response"])
