import streamlit as st
from gpt4all import GPT4All
from duckduckgo_search import DDGS
import yfinance as yf
import pandas as pd
import plotly.express as px
import pypdf
import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="SSGPT ULTRA", page_icon="💠", layout="wide")

# --- GUARDRAIL ENGINES ---
@st.cache_resource
def load_brain():
    try: return GPT4All("Llama-3.2-1B-Instruct-Q4_0.gguf")
    except: return None

def get_web_intel(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(f"{query} {datetime.date.today()}", max_results=3)
            return "\n".join([r['body'] for r in results])
    except: return "Global Search currently throttled."

# --- SIDEBAR (RESTORED & FIXED) ---
with st.sidebar:
    st.title("💠 SYSTEM CONTROL")
    st.markdown("---")
    st.subheader("📁 Document Vault")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    
    pdf_text = ""
    if uploaded_file:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            pdf_text = "\n".join([p.extract_text() for p in reader.pages[:3]])
            st.success(f"✅ {uploaded_file.name} Loaded")
        except: st.error("PDF Read Error")

# --- MAIN UI ---
st.markdown('<h1 style="text-align:center; color:#00f2ff;">SSGPT.v3 ULTRA 🌐</h1>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask for a stock graph, image, or video..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. GRAPH GUARDRAIL
        if any(x in prompt.lower() for x in ["graph", "chart", "stock"]):
            st.caption("📈 Fetching Market Intel...")
            ticker = "NVDA" if "nvidia" in prompt.lower() else "BTC-USD"
            data = yf.download(ticker, period="1mo")
            
            # FIX: Only draw if data exists!
            if not data.empty and len(data) > 0:
                fig = px.line(data, y="Close", title=f"{ticker} Analysis", template="plotly_dark")
                fig.update_traces(line_color='#00f2ff')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"⚠️ No market data found for {ticker}. Try a different ticker.")

        # 2. IMAGE/VIDEO GUARDRAIL
        elif any(x in prompt.lower() for x in ["image", "draw", "video"]):
            st.caption("🎨 Synthesizing Visuals...")
            # Use a timestamp seed to prevent "cached" old images
            seed = datetime.datetime.now().microsecond
            clean_prompt = prompt.replace(" ", "%20")
            
            if "video" in prompt.lower():
                url = f"https://pollinations.ai/p/{clean_prompt}?model=video&seed={seed}"
                st.video(url)
            else:
                url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed={seed}"
                st.image(url, caption="AI Render Complete")

        # 3. TEXT BRAIN (PDF + WEB)
        else:
            with st.spinner("Consulting Global Intel..."):
                web_info = get_web_intel(prompt)
                model = load_brain()
                context = f"PDF: {pdf_text}\n\nWeb: {web_info}"
                
                if model:
                    response = model.generate(f"Context: {context}\n\nUser: {prompt}", max_tokens=300)
                    st.markdown(response)
                else:
                    st.write(f"Direct Intel: {web_info[:500]}...")
