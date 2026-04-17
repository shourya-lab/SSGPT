import streamlit as st
import json, os, time
from groq import Groq

# --- CONFIG ---
st.set_page_config(page_title="SSGPT ULTRA", layout="wide")

# --- UI STYLE ---
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f0f0f, #1a1a2e);
    color: white;
}
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 12px;
    margin: 8px 0;
}
button {
    border-radius: 10px !important;
    background: linear-gradient(135deg, #ff0080, #7928ca) !important;
    color: white !important;
}
textarea, input {
    border-radius: 10px !important;
    background: #111 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
USER_DB = "ssgpt_ultra.json"

def load_db():
    if os.path.exists(USER_DB):
        try:
            return json.load(open(USER_DB, "r"))
        except:
            return {}
    return {}

def save_db(data):
    json.dump(data, open(USER_DB, "w"))

# --- AUDIO ENGINE ---
def trigger_audio(text, lang="en-US"):
    safe = text.replace('"', '').replace("\n", " ")
    st.components.v1.html(f"""
    <script>
    const msg = new SpeechSynthesisUtterance("{safe}");
    msg.lang = "{lang}";
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """, height=0)

# --- TYPEWRITER ---
def typewriter(text):
    box = st.empty()
    out = ""
    for c in text:
        out += c
        box.markdown(out)
        time.sleep(0.005)

# --- AUTH ---
if "auth" not in st.session_state:
    st.title("💠 SSGPT INITIALIZE")

    email = st.text_input("Email")
    lang = st.selectbox("Accent", ["en-US", "hi-IN", "de-DE"])

    st.markdown("### 🚀 Unlock PRO")
    st.markdown("Review us on **Product Hunt** to unlock premium features.")

    if st.button("CONNECT"):
        db = load_db()
        if email not in db:
            db[email] = {"lang": lang, "pro": False}
        save_db(db)

        st.session_state.auth = True
        st.session_state.email = email
        st.session_state.chat_history = []
        st.rerun()

    st.stop()

# --- LOAD USER ---
db = load_db()
user = db[st.session_state.email]

st.title("✨ SSGPT ULTRA" if user["pro"] else "💠 SSGPT TERMINAL")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    new_lang = st.selectbox(
        "🎙️ Accent",
        ["en-US", "hi-IN", "de-DE"],
        index=["en-US", "hi-IN", "de-DE"].index(user["lang"])
    )

    if new_lang != user["lang"]:
        user["lang"] = new_lang
        db[st.session_state.email] = user
        save_db(db)
        st.success("Accent updated")

# --- PRODUCT HUNT BANNER ---
st.markdown("""
### 🌟 Unlock PRO Access  
Review us on **Product Hunt** → Get:
- ⚡ Faster AI  
- 🔊 Better voice  
- 🧠 Memory mode  
- 🎨 Premium UI  
""")

# --- CHECK API KEY ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("🚨 Missing GROQ_API_KEY in secrets")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- CHAT HISTORY ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- INPUT ---
if prompt := st.chat_input("Ask anything..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            messages = st.session_state.chat_history

            res = client.chat.completions.create(
                messages=messages,
                model="llama3-70b-8192",  # ✅ FIXED MODEL
            )

            ans = res.choices[0].message.content

        except Exception as e:
            ans = f"❌ Error: {str(e)}"

        typewriter(ans)
        trigger_audio(ans, user["lang"])

        st.session_state.chat_history.append(
            {"role": "assistant", "content": ans}
        )
