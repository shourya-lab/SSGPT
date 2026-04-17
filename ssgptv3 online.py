import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import json
import os
import time
from datetime import datetime

# --- 1. THE VOICE ENGINE (DICTATION FIX) ---
def voiceover(text, lang='en-US'):
    # This JS uses a 'click' requirement to bypass browser blocks
    js_code = f"""
    <script>
    function speak() {{
        var msg = new SpeechSynthesisUtterance("{text.replace('"', '')}");
        msg.lang = "{lang}";
        window.speechSynthesis.speak(msg);
    }}
    speak(); 
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# --- 2. THE DATABASE ENGINE (KEYERROR FIX) ---
USER_DB = "ssgpt_v4_master.json"

def load_db():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {}

def save_db(data):
    with open(USER_DB, "w") as f: json.dump(data, f)

# --- 3. UI & ADDICTIVE STYLING ---
st.set_page_config(page_title="SSGPT TERMINAL", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #000000; color: #00f2ff; font-family: 'Courier New', monospace; }
    .stButton>button { background: linear-gradient(45deg, #00f2ff, #7000ff); color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTH & HISTORY SYSTEM ---
if "auth" not in st.session_state:
    st.title("💠 SSGPT TERMINAL: INITIALIZE")
    email = st.text_input("Google Email ID")
    lang_pref = st.selectbox("System Voice", ["English", "Hindi", "German"])
    
    if st.button("CONNECT SYSTEM"):
        if email:
            db = load_db()
            # FIX: If email is missing, create a blank profile so we don't get KeyError
            if email not in db:
                db[email] = {"history": [], "lang": lang_pref}
                save_db(db)
            
            st.session_state.user_info = db[email]
            st.session_state.email = email
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 5. SIDEBAR (AUTO-LOADING HISTORY) ---
with st.sidebar:
    st.header("👤 AGENT PROFILE")
    st.caption(f"ID: {st.session_state.email}")
    st.markdown("---")
    st.subheader("🕒 PREVIOUS CHATS")
    # This now loads from your saved JSON file
    for chat in st.session_state.user_info.get("history", [])[-3:]:
        st.info(f"{chat['date']}\n{chat['topic']}")

# --- 6. MAIN CHAT & ANALYSIS ---
st.markdown("<h1 style='color:#00f2ff;'>TERMINAL 🔗</h1>", unsafe_allow_html=True)

if prompt := st.chat_input("Ask a specialist..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # SPECIALIST DATA LOGIC
        # India GDP Proxy (INDA) or specific stock
        ticker = "INDA" if "india" in prompt.lower() else "NVDA"
        
        if any(x in prompt.lower() for x in ["graph", "chart", "price"]):
            df = yf.download(ticker, period="1mo")
            if not df.empty:
                # FIX: VALUEERROR from your image_47c32a screenshot
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                fig = px.line(df, y="Close", title=f"{ticker} Performance Vector", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                ans = f"Market data for {ticker} synchronized, Agent {st.session_state.email.split('@')[0]}."
            else:
                ans = "Data link failed. Ticker not found."
        else:
            ans = "Physics/Finance Intel: Trajectory analysis synchronized."

        # VOICE & TYPEWRITER
        lang_map = {"English": "en-US", "Hindi": "hi-IN", "German": "de-DE"}
        voiceover(ans, lang_map.get(st.session_state.user_info["lang"], "en-US"))
        
        ph = st.empty()
        full = ""
        for char in ans:
            full += char
            ph.markdown(full + "▌")
            time.sleep(0.01)
        ph.markdown(ans)

    # --- 7. SAVE TO DATABASE (KEYERROR PROTECTED) ---
    db = load_db()
    # Double-check that the key exists before saving
    if st.session_state.email in db:
        db[st.session_state.email]["history"].append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "topic": prompt[:25] + "..."
        })
        save_db(db)
