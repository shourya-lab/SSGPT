import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import json
import os
import time
import requests
from datetime import datetime

# --- 1. THE PERMANENT DATABASE ---
USER_DB = "ssgpt_v11_audiofix.json"

def load_db():
    if os.path.exists(USER_DB):
        try:
            with open(USER_DB, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(USER_DB, "w") as f: json.dump(data, f)

# --- 2. MULTILINGUAL VOICE ENGINE (FIXED) ---
def speak(text, lang_code='en-US'):
    # Sanitizing text to prevent Javascript breaks
    safe_text = text.replace("'", "").replace('"', "").replace("\n", " ")
    js_code = f"""
    <script>
    window.speechSynthesis.cancel();
    var msg = new SpeechSynthesisUtterance("{safe_text}");
    msg.lang = "{lang_code}";
    msg.rate = 1.0;
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# --- 3. DYNAMIC THEMES (PRO & NORMAL) ---
def apply_theme(is_pro):
    if is_pro: # Obsidian Gold
        primary, bg, text = "#FFD700", "#050505", "#FFFFFF"
        title = "✨ SSGPT ULTRA: PRO EDITION"
    else: # Cyberpunk Cyan
        primary, bg, text = "#00f2ff", "#000000", "#E0E0E0"
        title = "💠 SSGPT ULTRA: TERMINAL"
    
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg}; color: {text}; }}
        .stButton>button {{ 
            background: linear-gradient(45deg, {primary}, #000); 
            color: {primary}; border: 1px solid {primary};
            border-radius: 8px; font-weight: bold;
        }}
        .stChatInput {{ border: 1px solid {primary} !important; }}
        </style>
    """, unsafe_allow_html=True)
    return title

# --- 4. ONE-TIME LOGIN (Fixes image_492429) ---
if "auth" not in st.session_state:
    st.title("💠 INITIALIZE SSGPT")
    email = st.text_input("Enter Google Email ID")
    lang_pref = st.selectbox("Specialist Voice Language", ["en-US", "hi-IN", "de-DE"])
    
    if st.button("CONNECT SYSTEM"):
        if email:
            db = load_db()
            if email not in db: # Fixes KeyError
                db[email] = {"history": [], "lang": lang_pref, "pro": False}
                save_db(db)
            st.session_state.email = email
            st.session_state.auth = True
            st.session_state.chat_history = [] # Fixes vanishing chat
            st.rerun()
    st.stop()

# --- 5. SIDEBAR & REWARDS ---
db = load_db()
user_data = db[st.session_state.email]
terminal_title = apply_theme(user_data["pro"])

with st.sidebar:
    st.header(f"AGENT: {st.session_state.email.split('@')[0].upper()}")
    if not user_data["pro"]:
        st.info("🚀 Unlock Obsidian Gold Skin: Provide a 60+ character review on Product Hunt.")
        review = st.text_area("Paste Review:")
        if st.button("ACTIVATE PRO"):
            if len(review) > 60:
                user_data["pro"] = True
                save_db(db)
                st.rerun()
    st.link_button("👉 PRODUCT HUNT", "https://www.producthunt.com/posts/ssgpt")

# --- 6. MAIN TERMINAL & AUDIO FIX ---
st.title(terminal_title)

# Display Chat History
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])
        if chat["role"] == "assistant":
            if st.button("🔊 Re-play Voice", key=f"btn_{time.time()}"):
                speak(chat["content"], user_data["lang"])

if prompt := st.chat_input("Ask a specialist..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Graphing Specialist Logic
        if any(x in prompt.lower() for x in ["stock", "price", "graph"]):
            ticker = "NVDA" if "nvda" in prompt.lower() else "INDA"
            df = yf.download(ticker, period="1mo")
            if not df.empty:
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                fig = px.line(df, y="Close", title=f"{ticker} Analysis", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

        # AI Specialist Response via Ollama
        try:
            r = requests.post("http://localhost:11434/api/generate", 
                              json={"model": "llama3.2", "prompt": f"You are a specialist. Answer: {prompt}", "stream": False}, 
                              timeout=10)
            ans = r.json().get("response", "Analyzing data...")
        except:
            ans = "Ollama connection failed. Ensure server is active."

        # Trigger Auto-Voice and Manual Button
        speak(ans, user_data["lang"])
        st.markdown(ans)
        if st.button("🔊 Play Voiceover"):
            speak(ans, user_data["lang"])
        
        st.session_state.chat_history.append({"role": "assistant", "content": ans})
