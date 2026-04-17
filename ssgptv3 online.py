import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import json
import os
import time
import requests
from datetime import datetime

# --- 1. THE PERMANENT DATABASE (Fixes KeyErrors) ---
USER_DB = "ssgpt_v10_launch.json"

def load_db():
    if os.path.exists(USER_DB):
        try:
            with open(USER_DB, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(USER_DB, "w") as f: json.dump(data, f)

# --- 2. MULTILINGUAL VOICE ENGINE (Fixed punctuation & lang) ---
def speak(text, lang_code='en-US'):
    # Sanitizing to prevent JS breaks (Fix for previous silent failures)
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

# --- 3. ADDICTIVE DYNAMIC THEMES ---
def apply_theme(is_pro):
    if is_pro: # Obsidian Gold (Addictive Reward)
        primary, bg, text, glow = "#FFD700", "#050505", "#FFFFFF", "0 0 15px #FFD700"
        title = "✨ SSGPT ULTRA: PRO EDITION"
    else: # Cyberpunk Cyan (Standard)
        primary, bg, text, glow = "#00f2ff", "#000000", "#E0E0E0", "0 0 10px #00f2ff"
        title = "💠 SSGPT ULTRA: TERMINAL"
    
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg}; color: {text}; font-family: 'Segoe UI', sans-serif; }}
        .stButton>button {{ 
            background: linear-gradient(45deg, {primary}, #000); 
            color: {primary}; border: 1px solid {primary};
            border-radius: 8px; box-shadow: {glow}; font-weight: bold;
        }}
        .stChatInput {{ border: 1px solid {primary} !important; box-shadow: {glow}; border-radius: 12px; }}
        .sidebar .sidebar-content {{ background-color: {bg}; border-right: 1px solid {primary}; }}
        </style>
    """, unsafe_allow_html=True)
    return title

# --- 4. AUTH & ONE-TIME INITIALIZATION (Fixes image_492429) ---
if "auth" not in st.session_state:
    st.title("💠 INITIALIZE SSGPT")
    email = st.text_input("Enter Google Email ID")
    lang_pref = st.selectbox("Specialist Voice Language", ["en-US", "hi-IN", "de-DE", "ja-JP"])
    
    if st.button("CONNECT SYSTEM"):
        if email:
            db = load_db()
            # FIX: Create user profile if it doesn't exist to prevent KeyError
            if email not in db:
                db[email] = {"history": [], "lang": lang_pref, "pro": False}
                save_db(db)
            
            st.session_state.email = email
            st.session_state.auth = True
            st.session_state.chat_history = [] # For session persistence
            st.rerun()
    st.stop()

# --- 5. SIDEBAR & PRODUCT HUNT REWARDS ---
db = load_db()
user_data = db[st.session_state.email]
terminal_title = apply_theme(user_data["pro"])

with st.sidebar:
    st.header(f"AGENT: {st.session_state.email.split('@')[0].upper()}")
    
    if not user_data["pro"]:
        st.info("🚀 LAUNCH REWARD: Review on Product Hunt to unlock Obsidian Gold skin & 2x Memory.")
        review = st.text_area("Paste Review (Must mention a problem or improvement):")
        if st.button("UNLOCK PRO STATUS"):
            if len(review) > 60 and any(w in review.lower() for w in ["problem", "fix", "improve", "issue"]):
                user_data["pro"] = True
                save_db(db)
                st.balloons()
                st.rerun()
            else:
                st.error("Please provide a decent review (60+ chars) mentioning a problem or improvement.")
    else:
        st.success("✨ PRO ACCESS: OBSIDIAN SKIN & 12-MESSAGE MEMORY")
    
    st.link_button("👉 PRODUCT HUNT PAGE", "https://www.producthunt.com/posts/ssgpt")
    st.markdown("---")
    st.subheader("🕒 DATA HISTORY")
    for h in user_data["history"][-5:]:
        st.caption(f"{h['date']}: {h['topic']}")

# --- 6. MAIN CHAT TERMINAL (No Vanishing) ---
st.title(terminal_title)

# Display history so it doesn't vanish after graph renders
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if prompt := st.chat_input("Input query..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Graph & Accurate Answers Engine
        if any(x in prompt.lower() for x in ["stock", "price", "graph", "gdp"]):
            ticker = "INDA" if "india" in prompt.lower() else "NVDA"
            df = yf.download(ticker, period="1mo")
            if not df.empty:
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                fig = px.line(df, y="Close", title=f"{ticker} Specialist Trend", template="plotly_dark")
                fig.update_traces(line_color='#FFD700' if user_data["pro"] else '#00f2ff')
                st.plotly_chart(fig, use_container_width=True)
                ans_intro = f"Market vectors for {ticker} rendered. "
            else:
                ans_intro = "Market link failed. "
        else:
            ans_intro = ""

        # AI Specialist Response via Ollama
        try:
            # PRO gets 12 message context, normal gets 5
            limit = 12 if user_data["pro"] else 5
            context = st.session_state.chat_history[-limit:]
            r = requests.post("http://localhost:11434/api/generate", 
                              json={"model": "llama3.2", 
                                    "prompt": f"Specialist context: {context}\nUser: {prompt}\nResponse:", 
                                    "stream": False}, 
                              timeout=10)
            ai_ans = r.json().get("response", "Analyzing...")
        except:
            ai_ans = "Specialist Brain offline. Ensure 'ollama serve' is active."
        
        full_ans = ans_intro + ai_ans

        # Voiceover & Visual rendering
        speak(full_ans, user_data["lang"])
        ph = st.empty()
        curr = ""
        for char in full_ans:
            curr += char
            ph.markdown(curr + "▌")
            time.sleep(0.01)
        ph.markdown(full_ans)
        st.session_state.chat_history.append({"role": "assistant", "content": full_ans})

    # Save globally to the JSON DB
    db = load_db()
    db[st.session_state.email]["history"].append({"date": datetime.now().strftime("%H:%M"), "topic": prompt[:25]})
    save_db(db)
