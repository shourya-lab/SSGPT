import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
import PyPDF2
from openai import OpenAI

# --- CONFIG ---
st.set_page_config(page_title="SSGPT", layout="wide")

# --- API (FREE MODEL SAFE) ---
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# --- LANGUAGES ---
languages = {
    "en-US": "English","hi-IN": "Hindi","mr-IN": "Marathi","ta-IN": "Tamil",
    "te-IN": "Telugu","kn-IN": "Kannada","ml-IN": "Malayalam","bn-IN": "Bengali",
    "gu-IN": "Gujarati","pa-IN": "Punjabi","ur-PK": "Urdu","or-IN": "Odia",
    "as-IN": "Assamese","fr-FR": "French","de-DE": "German","es-ES": "Spanish",
    "it-IT": "Italian","nl-NL": "Dutch","ja-JP": "Japanese"
}

# --- SESSION ---
if "chat" not in st.session_state:
    st.session_state.chat = []
if "pro" not in st.session_state:
    st.session_state.pro = False
if "voice" not in st.session_state:
    st.session_state.voice = True

# --- UI THEMES ---
if st.session_state.pro:
    st.markdown("""
    <style>
    body {background: linear-gradient(135deg,#000,#1a0033);}
    button {
        background:linear-gradient(90deg,#ff00cc,#3333ff)!important;
        color:white!important;
        border-radius:12px!important;
    }
    button:hover {transform:scale(1.08);}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    body {background:#0f0f0f;}
    button:hover {transform:scale(1.05);}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Control Panel")

    lang = st.selectbox("🌍 Language", list(languages.keys()))

    st.session_state.voice = st.toggle("🔊 Voice", True)

    if st.button("⭐ Activate PRO"):
        st.session_state.pro = True

    uploaded_pdf = st.file_uploader("📄 Upload PDF")

# --- PDF READING ---
pdf_text = ""
if uploaded_pdf:
    reader = PyPDF2.PdfReader(uploaded_pdf)
    for page in reader.pages:
        pdf_text += page.extract_text()

# --- TITLE ---
st.title("✨ SSGPT PRO" if st.session_state.pro else "💠 SSGPT")

# ======================
# 📈 STOCK ANALYSIS
# ======================
st.subheader("📈 Stock Market")

ticker = st.text_input("Enter Stock (AAPL, TSLA, RELIANCE.NS)")

if ticker:
    data = yf.download(ticker, period="1mo")

    if not data.empty:
        st.line_chart(data["Close"])
        st.metric("Latest Price", f"{data['Close'].iloc[-1]:.2f}")

# ======================
# 📰 NEWS
# ======================
st.subheader("📰 Finance News")

feed = feedparser.parse("https://news.google.com/rss/search?q=finance")

for entry in feed.entries[:5]:
    st.markdown(f"**{entry.title}**")
    st.write(entry.link)

# ======================
# 💬 CHAT
# ======================
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- VOICE FUNCTION ---
def speak(text):
    safe = text.replace('"', '')
    st.components.v1.html(f"""
    <script>
    let msg = new SpeechSynthesisUtterance("{safe}");
    msg.lang = "{lang}";
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """, height=0)

# ======================
# 💬 INPUT
# ======================
if prompt := st.chat_input("Ask anything..."):

    st.session_state.chat.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):

        try:
            system = f"""
You are a Bloomberg-level AI.

Focus:
- Finance & stocks
- Global news
- Education

Give structured answers:
- Insight
- Key points
- Risks

Reply in {languages[lang]}.
"""

            messages = [{"role": "system", "content": system}] + st.session_state.chat

            if pdf_text:
                messages.append({
                    "role": "system",
                    "content": f"Use this document:\n{pdf_text[:3000]}"
                })

            # ✅ FREE MODEL (NO CREDIT ERROR)
            res = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct",
                messages=messages
            )

            ans = res.choices[0].message.content

        except Exception as e:
            ans = f"❌ Error: {str(e)}"

        st.markdown(ans)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔊 Speak"):
                speak(ans)

        with col2:
            if st.button("⛔ Stop"):
                st.components.v1.html(
                    "<script>speechSynthesis.cancel()</script>", height=0
                )

        st.session_state.chat.append({"role": "assistant", "content": ans})
