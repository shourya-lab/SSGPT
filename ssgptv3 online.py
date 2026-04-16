import streamlit as st
from gpt4all import GPT4All
from duckduckgo_search import DDGS
import random
import time

# --- SAFETY WRAPPERS FOR LIBRARIES ---
try:
    from youtubesearchpython import VideosSearch
    import pypdf
    import serial
except ImportError as e:
    st.error(f"Missing dependency: {e}. Check requirements.txt")
    st.stop()

# --- THE TECH-STACK STYLING ---
st.set_page_config(page_title="ssgpt Pro", page_icon="💠", layout="wide")

st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 2% 2%, rgba(0, 242, 255, 0.15), transparent 40%);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #7000ff;
    }

    /* Header Text */
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

    /* Chat Bubbles */
    .stChatMessage {
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        background: rgba(20, 20, 20, 0.8) !important;
        border-radius: 15px !important;
    }

    /* Status Notifications */
    .status-msg {
        color: #00ffa3;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- CORE LOGIC FUNCTIONS ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results) if results else "No real-time data found."
    except: return "Search engine currently offline."

@st.cache_resource
def load_engine():
    # Update this for local or remove path for Hugging Face Cloud
    model_name = "Llama-3.2-1B-Instruct-Q4_0.gguf"
    return GPT4All(model_name)

# --- HARDWARE SUPERVISOR (Safe Mode) ---
if "arduino" not in st.session_state:
    try:
        # Change 'COM3' to your specific port
        ser = serial.Serial(port='COM3', baudrate=9600, timeout=0.1)
        st.session_state.arduino = ser
    except:
        st.session_state.arduino = None

# --- UI LAYOUT ---
st.markdown('<h1 class="header-text">SSGPT.v3 PRO 💠</h1>', unsafe_allow_html=True)

# Sidebar: Document Vault & Hardware Status
with st.sidebar:
    st.title("💠 System Control")
    
    # Hardware Status
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
        # Extracts text from first 5 pages to avoid memory overflow
        file_context = "\n".join([p.extract_text() for p in reader.pages[:5]])
        st.info("Context Loaded: " + uploaded_file.name)

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.
