import streamlit as st
import pandas as pd
import google.generativeai as genai

#SETUP / Config
st.set_page_config(page_title="Assistant AI", page_icon="💬", layout="wide")

st.navigation(st.link_button( "Go to Home Page","https://build-a-space-biology-knowledge-engine-2wcmupfwpshtv4uv2oxfap.streamlit.app/", help=None, type="secondary", icon="🏠", disabled=False, width="content")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    MODEL_NAME = "gemini-2.5-flash"
except Exception as e:
    st.error(f"Error configuring Gemini AI: {e}")
    st.stop()

st.markdown("""
<style>
    /* HIDE STREAMLIT'S DEFAULT NAVIGATION */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stPageLink"] { display: none; } 
    
    /* Push content to the top */
    .block-container { padding-top: 1rem !important; }
    
    /* Remove custom nav button styling as we now use st.navigation */
    .nav-container { display: none; } 

    /* Main Theme */
    body { background-color: #FFFFFF; color: #333333; }
    h1 { color: #000000; text-align: center; }
    
    /* Styling for the input box */
    .stTextInput>div>div>input { 
        color: #000000 !important; 
        background-color: #F0F2F6 !important; 
        border: 1px solid #CCCCCC !important; 
        border-radius: 8px; 
        padding: 14px;
    }
    
    /* Purple links/text */
    a { color: #6A1B9A; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; }
    
    /* Style for the centered header text (to make 608 bold) */
    .centered-header-text strong {
        color: #6A1B9A;
    }
    </style>
""", unsafe_allow_html=True)

# helper
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv("SB_publication_PMC.csv", usecols=['Title', 'Link']) 
    except (FileNotFoundError, ValueError):
        st.error("Error: Could not load the publication data file (SB_publication_PMC.csv).")
        st.stop()

def find_relevant_publications(query, df, top_k=5):
    if query:
        mask = df["Title"].astype(str).str.lower().str.contains(query.lower(), na=False)
        return df[mask].head(top_k)
    return pd.DataFrame()

#main page
df = load_data("SB_publication_PMC.csv")

st.title("Assistant AI")
st.markdown(
    "<p class='centered-header-text' style='text-align: center;'>Ask me anything about the <strong>608 NASA bioscience publications</strong>.</p>", 
    unsafe_allow_html=True
)
_, col2, _ = st.columns([1, 2, 1])
with col2:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            with st.spinner("Searching publications and formulating answer..."):
                
                relevant_pubs = find_relevant_publications(prompt, df)
                
                if not relevant_pubs.empty:
                    # RAG Mode: Publications were found. Instruct AI to use them.
                    context_str = "Based on the following relevant publications:\n"
                    for _, row in relevant_pubs.iterrows():
                        context_str += f"- **Title:** {row['Title']}\n" 
                      
                    full_prompt = (
                        "You are a specialized AI assistant for NASA's bioscience research. "
                        "Answer the user's question based *only* on the context provided below. "
                        "If the context is insufficient, state clearly that you cannot find the answer based on the publications. "
                        "Explicitly cite the **titles** of the papers you reference.\n\n"
                        f"--- CONTEXT (Relevant Publication Titles) ---\n{context_str}\n\n"
                        f"--- USER'S QUESTION ---\n{prompt}"
                    )
                else:
                    full_prompt = (
                        "You are a specialized AI assistant. No specific NASA publications were found for the user's query in your database of 608 papers. "
                        "Therefore, answer the user's question accurately using your general knowledge about bioscience and space, "
                        "and clearly state at the beginning: 'Based on my general knowledge (as no matching NASA publications were found):'.\n\n"
                        f"--- USER'S QUESTION ---\n{prompt}"
                    )

                try:
                    model = genai.GenerativeModel(MODEL_NAME)
                    response = model.generate_content(full_prompt)
                    ai_response = response.text
                except Exception as e:
                    ai_response = f"Sorry, an error occurred with the AI service: {e}"
                
                placeholder.markdown(ai_response)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
