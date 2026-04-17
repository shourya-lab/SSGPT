import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import pypdf
import json
import os
import time
from datetime import datetime

# --- 1. GLOBAL MULTI-LANG VOICE (EN, HI, DE) ---
def voiceover(text, lang='en-US'):
    # lang options: 'en-US', 'hi-IN', 'de-DE'
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text.replace('"', '')}");
    msg.lang = "{lang}";
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# --- 2. THE DATABASE ENGINE (LOADS PREVIOUS CHATS) ---
USER_DB = "ssgpt_master_v3.json"

def load_user_data():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DB, "w") as f: json.dump(data, f)

# --- 3. UI SETUP ---
st.set_page_config(page_title="SSGPT ULTRA", layout="wide")
st.markdown("<style>.stApp { background: #050505; color: #00f2ff; }</style>", unsafe_allow_html=True)

# --- 4. LOGIN & PERSISTENCE GATE ---
if "auth" not in st.session_state:
    st.title("💠 SSGPT ULTRA: SECURE ACCESS")
    col1, col2 = st.columns(2)
    with col1: email = st.text_input("Google Email")
    with col2: lang_pref = st.selectbox("Voice Language", ["English", "Hindi", "German"])
    
    if st.button("INITIALIZE SYSTEM"):
        if email:
            db = load_user_data()
            # Restore user if they exist, otherwise create new
            st.session_state.user = db.get(email, {"history": [], "lang": lang_pref})
            st.session_state.email = email
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 5. SIDEBAR (HISTORY IS LOADED HERE) ---
with st.sidebar:
    st.header("👤 AGENT PROFILE")
    st.write(f"ID: {st.session_state.email}")
    st.markdown("---")
    st.subheader("🕒 PREVIOUS CHATS")
    # This now displays actual data from the JSON database
    for chat in st.session_state.user["history"][-3:]:
        with st.expander(f"📌 {chat['date']}"):
            st.write(chat['summary'])
    
    st.markdown("---")
    st.subheader("📁 PHYSICS/FINANCE VAULT")
    up_pdf = st.file_uploader("Upload Intel", type=["pdf"])

# --- 6. MAIN SPECIALIST BRAIN ---
st.title("💠 QUANTUM-FINANCE TERMINAL")

if prompt := st.chat_input("Ask a specialist..."):
    # Audio Beep
    st.markdown('<audio autoplay src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)
    
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # SMART DATA LOGIC (India GDP Fix)
        # If India GDP is requested, we use INDA (ETF) or custom logic
        if "india" in prompt.lower() and "gdp" in prompt.lower():
            ticker = "INDA"
            specialist_note = "Mapping India's Economic Trajectory via MSCI India Index."
        elif "physics" in prompt.lower():
            ticker = None
            specialist_note = "Applying First Principles: Entropy and Vector Analysis active."
        else:
            # Extract ticker or default
            ticker = "NVDA" 
            specialist_note = "Quantitative Market Model Synchronized."

        # RENDER GRAPH
        if ticker:
            df = yf.download(ticker, period="1mo")
            if not df.empty:
                # FIX FOR VALUEERROR in image_47c32a.png
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                fig = px.line(df, y="Close", title=f"{ticker} Performance Vector", template="plotly_dark")
                fig.update_traces(line_color='#00f2ff')
                st.plotly_chart(fig, use_container_width=True)
            
        # VOICE DICTATION (Based on login preference)
        lang_map = {"English": "en-US", "Hindi": "hi-IN", "German": "de-DE"}
        target_lang = lang_map.get(st.session_state.user["lang"], "en-US")
        voiceover(specialist_note, target_lang)

        # TYPEWRITER EFFECT
        ph = st.empty()
        full = ""
        for c in specialist_note:
            full += c
            ph.markdown(full + "▌")
            time.sleep(0.01)
        ph.markdown(specialist_note)

    # SAVE TO DATABASE FOR NEXT TIME
    db = load_user_data()
    db[st.session_state.email]["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": prompt[:30] + "..."
    })
    save_user_data(db)
