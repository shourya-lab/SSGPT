import streamlit as st
from gpt4all import GPT4All
from duckduckgo_search import DDGS
import yfinance as yf
from newspaper import Article
import pypdf
import datetime
import serial

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="SSGPT.v3 ULTRA", page_icon="🌐", layout="wide")

# --- POWER TOOLS ---
def global_search(query):
    try:
        with DDGS() as ddgs:
            today = datetime.date.today()
            results = [f"{r['title']}: {r['body']}" for r in ddgs.text(f"{query} {today}", max_results=5)]
            return "\n\n".join(results)
    except:
        return "Global Search currently offline."

def analyze_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return f"Content from {url}: {article.text[:1000]}"
    except:
        return "Could not read that specific URL."

@st.cache_resource
def load_engine():
    try:
        return GPT4All("Llama-3.2-1B-Instruct-Q4_0.gguf")
    except:
        return None

# --- SIDEBAR: CONTROL & UPLOAD ---
with st.sidebar:
    st.title("💠 System Control")
    
    # ARDUINO CHECK
    if "arduino" not in st.session_state:
        try:
            ser = serial.Serial(port='COM3', baudrate=9600, timeout=0.1)
            st.session_state.arduino = ser
            st.success("🤖 ARDUINO: ONLINE")
        except:
            st.session_state.arduino = None
            st.info("ℹ️ Web Mode: Arduino Offline")

    st.markdown("---")
    
    # THE UPLOAD TAB (RESTORED)
    st.subheader("📁 Document Vault")
    uploaded_file = st.file_uploader("Upload PDF for AI Context", type=["pdf"])
    
    file_context = ""
    if uploaded_file:
        reader = pypdf.PdfReader(uploaded_file)
        # Reads first 5 pages to keep the AI from getting overwhelmed
        file_context = "\n".join([p.extract_text() for p in reader.pages[:5]])
        st.success(f"✅ Loaded: {uploaded_file.name}")

# --- MAIN UI ---
st.markdown('<h1 style="text-align:center; color:#7000ff;">SSGPT.v3 ULTRA: GLOBAL INTEL 🌐</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# CHAT INPUT
if prompt := st.chat_input("Ask about 2026 news, stocks, or your uploaded PDF..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. GATHER DATA (WEB + PDF)
        web_info = ""
        if "http" in prompt:
            url = [w for w in prompt.split() if "http" in w][0]
            web_info = analyze_url(url)
        elif "stock" in prompt.lower() or "$" in prompt:
            ticker = prompt.split()[-1].strip("$").upper()
            stock = yf.Ticker(ticker)
            web_info = f"Price: ${stock.info.get('currentPrice', 'N/A')}. News: {global_search(ticker)}"
        else:
            web_info = global_search(prompt)

        # Combine Web Data with your Uploaded PDF Data
        combined_context = f"LATEST WEB DATA: {web_info}\n\nUPLOADED PDF DATA: {file_context}"

        # 2. AI GENERATION
        model = load_engine()
        system_instruction = f"Current Date: {datetime.date.today()}. You are an Expert AI. Use the provided LIVE and PDF data to answer."
        
        if model:
            with st.spinner("Analyzing all sources..."):
                full_prompt = f"{system_instruction}\n\nContext: {combined_context}\n\nUser: {prompt}\n\nAnswer:"
                response = model.generate(full_prompt, max_tokens=400)
        else:
            response = f"Here is the intel I gathered: \n\n {combined_context[:500]}..."

        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
