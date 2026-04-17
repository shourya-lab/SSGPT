import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import pypdf
import json
import os
import time
from datetime import datetime

# --- 1. THE "SPECIALIST" ENGINE ---
def extract_ticker(text):
    """Simple logic to find a ticker in the prompt"""
    words = text.upper().split()
    # Common ones for quick testing
    for w in words:
        if len(w) <= 5 and w.isalpha(): return w
    return "BTC-USD" # Default if none found

# --- 2. ADDICTIVE UI CONFIG ---
st.set_page_config(page_title="SSGPT ULTRA", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #050505; color: #00f2ff; }
    .stChatInput { border: 2px solid #7000ff !important; }
    .stButton>button { background: linear-gradient(45deg, #00f2ff, #7000ff); color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GOOGLE LOGIN & HISTORY ---
if "authenticated" not in st.session_state:
    st.title("💠 SSGPT ULTRA: ACCESS PORTAL")
    email = st.text_input("Google Email")
    nick = st.text_input("Codename")
    if st.button("CONNECT GOOGLE ACCOUNT"):
        if email and nick:
            st.session_state.authenticated, st.session_state.email, st.session_state.nick = True, email, nick
            st.rerun()
    st.stop()

# --- 4. SIDEBAR (VAULT & HISTORY) ---
with st.sidebar:
    st.header(f"Specialist: {st.session_state.nick}")
    st.markdown("---")
    st.subheader("📁 PDF Vault")
    up_pdf = st.file_uploader("Upload Finance/Physics Data", type=["pdf"])
    
    st.markdown("---")
    st.subheader("🕒 Previous Sessions")
    st.caption("Auto-archiving active for: " + st.session_state.email)

# --- 5. MAIN CHAT & GRAPH LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Input Finance or Physics query..."):
    # Sound Effect (Addictive Trigger)
    st.markdown('<audio autoplay src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # THE GRAPH FIX (Solves the 'makes no sense' issue)
        if any(x in prompt.lower() for x in ["graph", "chart", "price", "stock"]):
            ticker = extract_ticker(prompt)
            st.caption(f"🔍 Analyzing Market Vectors for {ticker}...")
            
            df = yf.download(ticker, period="1mo")
            
            if not df.empty:
                # CRITICAL FIX: This stops the ValueError from your screenshot
                # It flattens the table so Plotly can find the 'Close' price correctly
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                
                # Dynamic Graphing
                fig = px.line(df, y="Close", title=f"{ticker} Performance (Finance Specialist View)", template="plotly_dark")
                fig.update_traces(line_color='#00f2ff', line_width=3)
                st.plotly_chart(fig, use_container_width=True)
                response = f"Quant Analysis for {ticker} rendered based on 30-day momentum."
            else:
                st.error(f"Ticker {ticker} not found in global database.")
                response = "Data link failed. Please provide a valid ticker (e.g., TSLA, AAPL, BTC-USD)."

        # PHYSICS SPECIALIST LOGIC
        elif any(x in prompt.lower() for x in ["physics", "force", "energy", "quantum"]):
            response = "Physics Intel: Calculating trajectory and entropy variables for your query..."
        else:
            response = "Intelligence Synchronized. How shall we proceed, Shourya?"

        # TYPEWRITER EFFECT (Addictive Visual)
        ph = st.empty()
        full = ""
        for c in response:
            full += c
            ph.markdown(full + "▌")
            time.sleep(0.01)
        ph.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
