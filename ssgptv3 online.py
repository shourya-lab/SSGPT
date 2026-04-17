import streamlit as st
import json, os, time
from groq import Groq

# --- CONFIG ---
st.set_page_config(page_title="SSGPT ULTRA", layout="wide")

# --- UI DESIGN (ADDICTIVE THEME) ---
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f0f0f, #1a1a2e);
    color: white;
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 14px;
    margin: 10px 0;
    backdrop-filter: blur(12px);
}

/* User */
[data-testid="stChatMessage"]:has(div[data-testid="stMarkdownContainer"]:first-child) {
    background: linear-gradient(135deg, #007cf0, #00dfd8);
}

/* Assistant */
[data-testid="stChatMessage"]:has(div[data-testid="stMarkdownContainer"]:last-child) {
    background: linear-gradient(135deg, #7928ca, #ff0080);
}

/* Buttons */
button {
    border-radius: 12px !important;
    background: linear-gradient(135deg, #ff0080, #7928ca) !important;
    color: white !important;
    border: none !important;
}

/* Inputs */
textarea, input {
    border-radius: 12px !important;
    background-color: #111 !important;
    color: white !important;
}

/* Title Glow */
h1 {
    text-align: center;
    font-weight: 900;
    background: linear-gradient(90deg, #00dfd8, #007cf0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
USER_DB = "ssgpt_ultra_safe.json"

def load_db():
    if os.path.exists(USER_DB):
        try:
            return json.load(open(USER_DB, "r"))
        except:
            return {}
    return {}

def save_db(data):
    json.dump(data, open(USER_DB, "w"))

# --- AUDIO ENGINE (FIXED) ---
def trigger_audio(text, lang="en-US"):
    safe = text.replace('"', '').replace("'", "")
    st.components.v1.html(f"""
    <script>
    const msg = new SpeechSynthesisUtterance("{safe}");
    msg.lang = "{lang}";
    msg.rate = 1;
    msg.pitch = 1;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """, height=0)

# --- TYPEWRITER EFFECT ---
def typewriter(text):
    box = st.empty()
    output = ""
    for char in text:
        output += char
        box.markdown(output)
        time.sleep(0.01)

# --- AUTH SCREEN ---
if "auth" not in st.session_state:
    st.title("💠 SSGPT INITIALIZE")

    email = st.text_input("Email ID")
    lang = st.selectbox("Accent", ["en-US", "hi-IN", "de-DE"])

    st.markdown("### 🚀 Launch Bonus")
    st.markdown(
        "👉 Leave us a review on **Product Hunt** and unlock **SSGPT PRO Mode + Priority AI Speed ⚡**"
    )

    if st.button("CONNECT"):
        db = load_db()
        if email not in db:
            db[email] = {"history": [], "lang": lang, "pro": False}
        save_db(db)

        st.session_state.email = email
        st.session_state.auth = True
        st.session_state.chat_history = []
        st.rerun()

    st.stop()

# --- LOAD USER ---
db = load_db()
user = db[st.session_state.email]

st.title("✨ SSGPT ULTRA" if user["pro"] else "💠 SSGPT TERMINAL")

# --- PRODUCT HUNT REWARD BANNER ---
st.markdown("""
### 🌟 Unlock PRO Access  
🔥 Review us on **Product Hunt** → Get:
- ⚡ Faster AI responses  
- 🔊 Premium voice engine  
- 🧠 Smart memory mode  
- 🎨 Exclusive UI skin  

👉 DM your review screenshot to activate PRO
""")

# --- CHAT HISTORY ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask anything..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])

            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )

            ans = res.choices[0].message.content

        except:
            ans = "🔒 Add GROQ_API_KEY in Streamlit Secrets."

        # Typewriter effect
        typewriter(ans)

        # AUTO VOICE PLAY (FIXED)
        trigger_audio(ans, user["lang"])

        st.session_state.chat_history.append(
            {"role": "assistant", "content": ans}
        )
