import streamlit as st
from gpt4all import GPT4All
from duckduckgo_search import DDGS
import yfinance as yf
from newspaper import Article
import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="SSGPT.v3 ULTRA", page_icon="🌐", layout="wide")

# --- POWER TOOLS ---
def global_search(query):
    """Searches 2026 live web for news, facts, and events"""
    try:
        with DDGS() as ddgs:
            # We add the current date to the query to force 2026 results
            today = datetime.date.today()
            results = [f"{r['title']}: {r['body']}" for r in ddgs.text(f"{query} {today}", max_results=5)]
            return "\n\n".join(results)
    except:
        return "Global Search currently offline."

def analyze_url(url):
    """Goes to a specific website and reads the content for the AI"""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return f"Content from {url}: {article.text[:1000]}"
    except:
        return "Could not read that specific URL."

# --- AI BRAIN ---
@st.cache_resource
def load_engine():
    try:
        return GPT4All("Llama-3.2-1B-Instruct-Q4_0.gguf")
    except:
        return None

# --- UI ---
st.markdown('<h1 style="text-align:center; color:#7000ff;">SSGPT.v3 ULTRA: GLOBAL INTEL 🌐</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about 2026 news, stocks, tech, or paste a URL..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        context = ""
        # 1. SMART TOOL SELECTION
        if "http" in prompt:
            st.caption("🌐 Accessing External URL...")
            url = [w for w in prompt.split() if "http" in w][0]
            context = analyze_url(url)
        elif "stock" in prompt.lower() or "$" in prompt:
            st.caption("📈 Analyzing Market Data...")
            ticker = prompt.split()[-1].strip("$").upper()
            stock = yf.Ticker(ticker)
            context = f"Live {ticker} Price: ${stock.info.get('currentPrice', 'N/A')}. News: {global_search(ticker)}"
        else:
            st.caption("🔍 Searching Global 2026 Databases...")
            context = global_search(prompt)

        # 2. GENERATE RESPONSE
        model = load_engine()
        system_instruction = f"Current Date: {datetime.date.today()}. You are a 2026 Super-AI. Use this LIVE DATA to answer accurately: {context}"
        
        if model:
            with st.spinner("Synthesizing Intel..."):
                full_prompt = f"{system_instruction}\n\nUser Question: {prompt}\n\nExpert Answer:"
                response = model.generate(full_prompt, max_tokens=400)
        else:
            response = f"I found the latest info for you! Here is the data: \n\n {context}"

        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
