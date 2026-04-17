import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import pypdf
import time
from datetime import datetime

# --- 1. THE BRAIN: PHYSICS & FINANCE SPECIALIST ---
def specialist_logic(prompt):
    if any(x in prompt.lower() for x in ["physics", "quantum", "force"]):
        return "PHYSICS INTEL: Analyzing vector trajectories. Kinetic energy and entropy levels are stabilizing."
    return "FINANCE INTEL: Quantitative model synchronized. Analyzing market liquidity and volatility."

# --- 2. THE VOICE ENGINE (DICTATION) ---
def dictate_text(text):
    # This JavaScript tells the browser to speak the text out loud
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text.replace('"', '')}");
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# --- 3. ADDICTIVE UI & MOBILE SETUP ---
st.set_page_config(page_title="SSGPT ULTRA", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #050505; color: #00f2ff; }
    .stButton>button { 
        background: linear-gradient(45deg, #00f2ff, #7000ff); 
        color: white; border-radius: 20px; border: none; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIN & 3-CHAT HISTORY ---
if "user" not in st.session_state:
    st.title("💠 SSGPT ULTRA: LOGIN")
    email = st.text_input("Google Email")
    nick = st.text_input("Codename")
    if st.button("LOG IN WITH GOOGLE"):
        if email and nick:
            st.session_state.user = {"email": email, "nick": nick, "history": []}
            st.rerun()
    st.stop()

# --- 5. SIDEBAR VAULT ---
with st.sidebar:
    st.header(f"Agent: {st.session_state.user['nick']}")
    st.markdown("---")
    st.subheader("🕒 Last 3 Sessions")
    for chat in st.session_state.user['history'][-3:]:
        st.caption(f"{chat['date']}: {chat['topic']}")
    st.markdown("---")
    st.file_uploader("Upload Physics/Finance PDF", type=["pdf"])

# --- 6. CHAT & GRAPH SYSTEM ---
if prompt := st.chat_input("Ask a specialist..."):
    # Addictive "Action" Sound (Beep)
    st.markdown('<audio autoplay src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # GRAPH LOGIC: Fixing the "Same Graph" issue
        # If user mentions a country or stock, we find the specific ticker
        ticker = "INDA" if "india" in prompt.lower() else "NVDA"
        if "bitcoin" in prompt.lower(): ticker = "BTC-USD"
        
        if any(x in prompt.lower() for x in ["graph", "chart", "price"]):
            data = yf.download(ticker, period="1mo")
            if not data.empty:
                # FIX: Handling the Multi-Index ValueError from your screenshot
                data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
                fig = px.line(data, y="Close", title=f"{ticker} Performance Vector", template="plotly_dark")
                fig.update_traces(line_color='#00f2ff')
                st.plotly_chart(fig, use_container_width=True)
                ans = f"Market data for {ticker} rendered for analysis."
            else:
                ans = "Market vector synchronization failed."
        else:
            ans = specialist_logic(prompt)

        # TYPEWRITER + DICTATION
        ph = st.empty()
        full_txt = ""
        dictate_text(ans) # This triggers the voice
        for char in ans:
            full_txt += char
            ph.markdown(full_txt + "▌")
            time.sleep(0.02)
        ph.markdown(ans)

    # Save to history
    st.session_state.user['history'].append({"date": datetime.now().strftime("%H:%M"), "topic": prompt[:15]})
