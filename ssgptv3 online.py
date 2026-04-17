import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import json, os, time
from groq import Groq
from datetime import datetime

# --- 1. CORE DATABASE ---
USER_DB = "ssgpt_ultra_safe.json"
def load_db():
    if os.path.exists(USER_DB):
        try: return json.load(open(USER_DB, "r"))
    except: return {}
    return {}

def save_db(data):
    json.dump(data, open(USER_DB, "w"))

# --- 2. THE AUDIO ENGINE ---
def trigger_audio(text, lang_code='en-US'):
    safe_text = text.replace("'", "").replace('"', "").replace("\n", " ")
    st.markdown(f"""
    <script>
    window.speechSynthesis.cancel();
    var msg = new SpeechSynthesisUtterance("{safe_text}");
    msg.lang = "{lang_code}";
    window.speechSynthesis.speak(msg);
    </script>
    """, unsafe_allow_html=True)

# --- 3. AUTH & UI ---
if "auth" not in st.session_state:
    st.title("💠 SSGPT INITIALIZE")
    email = st.text_input("Email ID")
    lang = st.selectbox("Accent", ["en-US", "hi-IN", "de-DE"])
    if st.button("CONNECT"):
        db = load_db()
        if email not in db: db[email] = {"history": [], "lang": lang, "pro": False}
        save_db(db); st.session_state.email = email; st.session_state.auth = True; st.session_state.chat_history = []; st.rerun()
    st.stop()

db = load_db(); user = db[st.session_state.email]
st.title("✨ SSGPT ULTRA" if user["pro"] else "💠 SSGPT TERMINAL")

# --- 4. THE CHAT ---
for i, msg in enumerate(st.session_state.chat_history):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button("🔊 Listen", key=f"v_{i}"): trigger_audio(msg["content"], user["lang"])

if prompt := st.chat_input("Ask..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # SAFETY SECURED: Key is pulled from Streamlit Dashboard Secrets
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            ans = res.choices[0].message.content
        except Exception as e:
            ans = "🔒 Security Alert: Please add 'GROQ_API_KEY' to your Streamlit Cloud Secrets."

        st.markdown(ans)
        if st.button("🔊 Play Voiceover", key="btn_now"): trigger_audio(ans, user["lang"])
        st.session_state.chat_history.append({"role": "assistant", "content": ans})
