import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import pypdf
import time
import datetime

# --- 1. MOBILE-FIRST UI CONFIG ---
st.set_page_config(page_title="SSGPT SPECIALIST", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Mobile Optimization */
    .main .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    
    /* Neon Physics/Finance Aesthetic */
    .stApp { background: radial-gradient(circle, #050505 0%, #001122 100%); color: #e0e0e0; }
    
    /* Glowing Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        background: linear-gradient(90deg, #00f2ff, #0077ff);
        color: white;
        border: none;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
        font-weight: bold;
    }
    
    /* Addictive Floating Voice Button for Mobile */
    .voice-btn {
        position: fixed;
        bottom: 80px;
        right: 20px;
        background: #00f2ff;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 0 20px #00f2ff;
        z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SPECIALIST KNOWLEDGE BASE ---
def specialist_brain(prompt, context=""):
    # This is the "Specialist" instruction layer
    system_instruction = (
        "You are SSGPT, a dual specialist in Quant Finance and Theoretical Physics. "
        "Use mathematical precision. If asked about stocks, provide volatility analysis. "
        "If asked about physics, explain using first principles (entropy, forces, quantum mechanics). "
        "Keep answers concise but high-level."
    )
    # Here you would call your GPT4All model.generate() 
    # For this demo, we'll simulate the specialist response:
    return f"ANALYSIS (Finance/Physics Delta): Based on the data, the trajectory follows a {prompt} pattern with high momentum."

# --- 3. THE SIDEBAR (Vault & Profile) ---
with st.sidebar:
    st.title("👤 CODENAME: SHOURYA")
    st.markdown("---")
    st.subheader("📚 Physics/Finance Library")
    up_file = st.file_uploader("Upload PDF Paper/Report", type=["pdf"])
    
    if up_file:
        st.success("Intel Synchronized.")

# --- 4. MAIN INTERFACE ---
st.markdown("<h2 style='text-align: center; color: #00f2ff;'>SSGPT: QUANTUM-FINANCE 💠</h2>", unsafe_allow_html=True)

# Addictive Typewriter Effect for Mobile
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Systems Online. Awaiting Finance or Physics query..."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- 5. THE INPUT & SOUND ---
if prompt := st.chat_input("Say 'Hey SSGPT' or type query..."):
    # Sound Effect (Web-based beep for mobile compatibility)
    st.markdown('<audio autoplay src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # SPECIALIST LOGIC: STOCKS
        if any(x in prompt.lower() for x in ["stock", "market", "price", "graph"]):
            ticker = "NVDA" if "nvidia" in prompt.lower() else "TSLA"
            data = yf.download(ticker, period="1mo")
            if not data.empty:
                # FIXED: Handling Multi-index for Mobile Plotly
                data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
                fig = px.line(data, y="Close", title=f"{ticker} Momentum Vector", template="plotly_dark")
                fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300) # Compact for Mobile
                st.plotly_chart(fig, use_container_width=True)
                response = f"Quant Analysis: {ticker} showing specific resistance levels."
            else:
                response = "Unable to fetch market vectors."
        
        # SPECIALIST LOGIC: PHYSICS / GENERAL
        else:
            response = specialist_brain(prompt)
            
        # Addictive Typewriter Output
        placeholder = st.empty()
        full_res = ""
        for char in response:
            full_res += char
            placeholder.markdown(full_res + "▌")
            time.sleep(0.02)
        placeholder.markdown(full_res)
        
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- 6. MOBILE VOICE TRIGGER (Visual Only) ---
st.markdown('<div class="voice-btn">🎙️</div>', unsafe_allow_html=True)
