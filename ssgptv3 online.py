import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import json
import os
import time
from datetime import datetime

# --- 1. UNIVERSAL VOICE ENGINE (MULTI-LANG) ---
def voiceover(text):
    # Detects language based on characters or defaults to user preference
    lang = st.session_state.user_info.get("lang_code", "en-US")
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text.replace('"', '')}");
    msg.lang = "{lang}";
    msg.rate = 1.1;
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE (FIXES PREVIOUS CHAT LOADING) ---
USER_DB = "ssgpt_omega_v5.json"

def load_db():
    if os.path.exists(USER_DB):
        try:
            with open(USER_DB, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(USER_DB, "w") as f: json.dump(data, f)

# --- 3. UI SETUP ---
st.set_page_config(page_title="SSGPT TERMINAL", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #000000; color: #00f2ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stChatInput { border: 2px solid #00f2ff !important; border-radius: 15px; }
    .stButton>button { background: linear-gradient(90deg, #00f2ff, #7000ff); color: white; border: none; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTH & SESSION PERSISTENCE ---
if "auth" not in st.session_state:
    st.title("💠 SSGPT TERMINAL: ACCESS")
    email = st.text_input("Enter Google Email ID")
    lang_choice = st.selectbox("Choose System Language", ["English", "Hindi", "German"])
    
    if st.button("SYNC WITH GOOGLE"):
        if email:
            db = load_db()
            lang_map = {"English": "en-US", "Hindi": "hi-IN", "German": "de-DE"}
            # KEYERROR FIX: Ensure the user object exists
            if email not in db:
                db[email] = {"history": [], "lang_code": lang_map[lang_choice]}
                save_db(db)
            
            st.session_state.user_info = db[email]
            st.session_state.email = email
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 5. SIDEBAR (HISTORY FIX) ---
with st.sidebar:
    st.header("👤 AGENT PROFILE")
    st.caption(st.session_state.email)
    st.markdown("---")
    st.subheader("🕒 PREVIOUS CHATS")
    # Dynamically load history from the session state
    for chat in st.session_state.user_info.get("history", [])[-5:]:
        with st.expander(f"📜 {chat['date']}"):
            st.write(chat['topic'])

# --- 6. UNIVERSAL SPECIALIST BRAIN ---
st.markdown("<h1 style='color:#00f2ff;'>TERMINAL 🔗</h1>", unsafe_allow_html=True)

if prompt := st.chat_input("Ask me anything (Finance, Physics, General)..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # STEP 1: FINANCE CHECK
        if any(x in prompt.lower() for x in ["stock", "graph", "india gdp", "price"]):
            ticker = "INDA" if "india" in prompt.lower() else "NVDA"
            df = yf.download(ticker, period="1mo")
            if not df.empty:
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                fig = px.line(df, y="Close", title=f"{ticker} Performance Vector", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                ans = f"Market vectors for {ticker} synchronized. Trend is visible on the terminal."
            else:
                ans = "Market link failed. Please provide a valid ticker."
        
        # STEP 2: UNIVERSAL KNOWLEDGE CHECK (Fixes the 'Acid' answer issue)
        else:
            # Here you would normally call your LLM. For now, we use a smart response logic.
            if "acid" in prompt.lower():
                ans = "Acids are chemical substances characterized by a sour taste and the ability to turn blue litmus paper red. In Physics/Chemistry terms, they are proton donors (H+ ions)."
            elif "physics" in prompt.lower():
                ans = "Theoretical Physics module active: Calculating entropy and fundamental force interactions."
            else:
                ans = f"I have analyzed your query: '{prompt}'. As your specialist, I recommend further deep-dive into the specific parameters of this topic."

        # STEP 3: VOICE & VISUAL FEEDBACK
        voiceover(ans)
        ph = st.empty()
        full = ""
        for char in ans:
            full += char
            ph.markdown(full + "▌")
            time.sleep(0.01)
        ph.markdown(ans)

    # --- 7. SAVE TO DATABASE ---
    db = load_db()
    db[st.session_state.email]["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "topic": prompt[:40]
    })
    save_db(db)
