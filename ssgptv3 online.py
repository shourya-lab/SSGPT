import streamlit as st
from gpt4all import GPT4All
from duckduckgo_search import DDGS
import random
import time

# --- SAFETY WRAPPERS FOR LIBRARIES ---
try:
    # FIX: Ensure these match your requirements.txt names
    from youtube_search_python import VideosSearch 
    import pypdf
    # NOTE: 'pyserial' is the library name, but you 'import serial'
    import serial 
except ImportError as e:
    st.error(f"Missing dependency: {e}. Check requirements.txt")
    st.stop()

# --- THE TECH-STACK STYLING ---
st.set_page_config(page_title="ssgpt Pro", page_icon="💠", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 2% 2%, rgba(0, 242, 255, 0.15), transparent 40%);
    }
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #7000ff;
    }
    .header-text {
        font-family: 'Courier New', monospace;
        background: linear-gradient(90deg, #00f2ff, #7000ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 30px;
    }
    .stChatMessage {
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        background: rgba(20, 20, 20, 0.8) !important;
        border-radius: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CORE LOGIC FUNCTIONS ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results) if results else "No real-time data found."
    except Exception: 
        return "Search engine currently offline."

@st.cache_resource
def load_engine():
    # WARNING: This file is huge (~1GB). 
    # Streamlit Cloud might struggle to download it every time.
    model_name = "Llama-3.2-1B-Instruct-Q4_0.gguf"
    try:
        return GPT4All(model_name)
    except Exception as e:
        st.error(f"Model Load Error: {e}")
        return None

# --- HARDWARE SUPERVISOR ---
if "arduino" not in st.session_state:
    try:
        # COM3 only works on your Windows PC, not on the Web/Cloud.
        ser = serial.Serial(port='COM3', baudrate=9600, timeout=0.1)
        st.session_state.arduino = ser
    except:
        st.session_state.arduino = None

# --- UI LAYOUT ---
st.markdown('<h1 class="header-text">SSGPT.v3 PRO 💠</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.title("💠 System Control")
    if st.session_state.arduino:
        st.success("🤖 ARDUINO: ONLINE (COM3)")
    else:
        st.warning("⚠️ ARDUINO: OFFLINE (Local Port Only)")

    st.markdown("---")
    st.subheader("📁 Document Vault")
    uploaded_file = st.file_uploader("Sync PDF Context", type=["pdf"])
    
    file_context = ""
    if uploaded_file:
        reader = pypdf.PdfReader(uploaded_file)
        file_context = "\n".join([p.extract_text() for p in reader.pages[:5]])
        st.info("Context Loaded: " + uploaded_file.name)

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# FIXED LINE 117: Added the full command
if prompt := st.chat_input("Type your message here..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = "I am processing your request..." # Replace with model logic
        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
