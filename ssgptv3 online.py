import streamlit as st
from gpt4all import GPT4All
from duckduckgo_search import DDGS
import yfinance as yf
import pandas as pd
import plotly.express as px
import pypdf
import datetime
import requests

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="SSGPT.v3 ALL-IN-ONE", page_icon="💠", layout="wide")

# --- CORE ENGINES ---
@st.cache_resource
def load_ai():
    try: return GPT4All("Llama-3.2-1B-Instruct-Q4_0.gguf")
    except: return None

def get_web_intel(query):
    try:
        with DDGS() as ddgs:
            return "\n".join([r['body'] for r in ddgs.text(f"{query} {datetime.date.today()}", max_results=3)])
    except: return "Web search currently unavailable."

# --- SIDEBAR: THE VAULT (RESTORED) ---
with st.sidebar:
    st.title("💠 SSGPT CONTROL")
    st.markdown("---")
    st.subheader("📁 Document Vault")
    uploaded_file = st.file_uploader("Upload PDF for Analysis", type=["pdf"])
    
    pdf_text = ""
    if uploaded_file:
        reader = pypdf.PdfReader(uploaded_file)
        pdf_text = "\n".join([p.extract_text() for p in reader.pages[:5]])
        st.success(f"Loaded: {uploaded_file.name}")

# --- MAIN INTERFACE ---
st.markdown('<h1 style="text-align:center; color:#00f2ff;">SSGPT.v3 ULTRA: MULTIMODAL 🌐</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask for a graph, generate an image, or analyze my PDF..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. GRAPH LOGIC
        if "graph" in prompt.lower() or "chart" in prompt.lower():
            st.caption("📈 Generating Data Analysis...")
            ticker = "BTC-USD" if "bitcoin" in prompt.lower() else "TSLA"
            data = yf.download(ticker, period="1mo")
            fig = px.line(data, y="Close", title=f"{ticker} Performance", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            response = f"I've generated the {ticker} analysis graph for you based on the last 30 days of market data."

        # 2. IMAGE LOGIC
        elif "image" in prompt.lower() or "draw" in prompt.lower():
            st.caption("🎨 Rendering AI Visual...")
            img_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed={datetime.datetime.now().microsecond}"
            st.image(img_url, caption=f"Generated: {prompt}")
            response = "Visual synthesis complete. See the generated image above."

        # 3. VIDEO LOGIC
        elif "video" in prompt.lower():
            st.caption("🎬 Processing AI Video...")
            vid_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?model=video"
            st.video(vid_url)
            response = "Video generation complete. High-quality motion render displayed above."

        # 4. GENERAL AI + PDF + WEB LOGIC
        else:
            with st.spinner("Analyzing web and documents..."):
                web_info = get_web_intel(prompt)
                full_context = f"PDF Info: {pdf_text}\n\nWeb Info: {web_info}"
                model = load_ai()
                if model:
                    response = model.generate(f"Context: {full_context}\n\nUser: {prompt}", max_tokens=300)
                else:
                    response = f"I found this for you: {web_info[:500]}"
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
