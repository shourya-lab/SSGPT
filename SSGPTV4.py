import streamlit as st
import json, os, time
from openai import OpenAI
import PyPDF2

# --- CONFIG ---
st.set_page_config(page_title="SSGPT", layout="wide")

# --- API ---
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# --- LANGUAGES (22+ INDIAN + GLOBAL) ---
languages = {
    "en-US": "English",
    "hi-IN": "Hindi",
    "mr-IN": "Marathi",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "bn-IN": "Bengali",
    "gu-IN": "Gujarati",
    "pa-IN": "Punjabi",
    "ur-PK": "Urdu",
    "or-IN": "Odia",
    "as-IN": "Assamese",
    "sa-IN": "Sanskrit",
    "fr-FR": "French",
    "de-DE": "German",
    "es-ES": "Spanish",
    "nl-NL": "Dutch",
    "it-IT": "Italian",
    "ja-JP": "Japanese",
    "ko-KR": "Korean"
}

# --- SESSION ---
if "chat" not in st.session_state:
    st.session_state.chat = []

if "pro" not in st.session_state:
    st.session_state.pro = False

if "voice_on" not in st.session_state:
    st.session_state.voice_on = True

# --- UI THEMES ---
def apply_theme(pro=False):
    if pro:
        st.markdown("""
        <style>
        body {background: linear-gradient(135deg,#000,#1a0033);}
        .stChatMessage {border-radius:18px;}
        button {background:linear-gradient(90deg,#ff00cc,#3333ff)!important;color:white;}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        body {background:#0f0f0f;}
        button:hover {transform:scale(1.05);}
        </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.pro)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Control")

    lang = st.selectbox("🌍 Language", list(languages.keys()))

    st.session_state.voice_on = st.toggle("🔊 Voice", True)

    if st.button("⭐ Activate PRO"):
        st.session_state.pro = True

    uploaded_pdf = st.file_uploader("📄 Upload PDF")

# --- PDF ---
pdf_text = ""
if uploaded_pdf:
    reader = PyPDF2.PdfReader(uploaded_pdf)
    for p in reader.pages:
        pdf_text += p.extract_text()

# --- TITLE ---
title = "✨ SSGPT PRO" if st.session_state.pro else "💠 SSGPT"
st.title(title)

# --- CHAT DISPLAY ---
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- VOICE ---
def speak(text):
    safe = text.replace('"','')
    st.components.v1.html(f"""
    <script>
    let msg = new SpeechSynthesisUtterance("{safe}");
    msg.lang = "{lang}";
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """, height=0)

# --- INPUT ---
if prompt := st.chat_input("Ask anything..."):

    st.session_state.chat.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):

        try:
            system = f"""
You are an expert AI.
Focus:
- Finance
- Global news
- Studies

Reply in {languages[lang]}.
Keep answers clear, intelligent, and structured.
"""

            messages = [{"role": "system", "content": system}] + st.session_state.chat

            if pdf_text:
                messages.append({
                    "role": "system",
                    "content": f"Use this document:\n{pdf_text[:3000]}"
                })

            res = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=messages
            )

            ans = res.choices[0].message.content

        except Exception as e:
            ans = f"❌ {str(e)}"

        st.markdown(ans)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔊 Speak"):
                speak(ans)

        with col2:
            if st.button("⛔ Stop"):
                st.components.v1.html(
                    "<script>speechSynthesis.cancel()</script>", height=0
                )

        st.session_state.chat.append({"role": "assistant", "content": ans})
