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

# --- LANGUAGE MAP ---
lang_map = {
    "en-US": "English",
    "hi-IN": "Hindi",
    "de-DE": "German",
    "fr-FR": "French",
    "nl-NL": "Dutch",
    "mr-IN": "Marathi",
    "kn-IN": "Kannada"
}

# --- AUDIO ENGINE (IMPROVED) ---
def trigger_audio(text, lang="en-US"):
    safe = text.replace('"', '').replace("\n", " ")

    st.components.v1.html(f"""
    <script>
    const speak = () => {{
        const voices = speechSynthesis.getVoices();

        let selectedVoice = voices.find(v => v.lang === "{lang}");

        if (!selectedVoice) {{
            selectedVoice = voices.find(v => v.lang.startsWith("{lang.split('-')[0]}"));
        }}

        const msg = new SpeechSynthesisUtterance("{safe}");
        if (selectedVoice) msg.voice = selectedVoice;

        msg.lang = "{lang}";
        msg.rate = 1;

        speechSynthesis.cancel();
        speechSynthesis.speak(msg);
    }};

    speechSynthesis.onvoiceschanged = speak;
    speak();
    </script>
    """, height=0)

# --- TYPEWRITER ---
def typewriter(text):
    box = st.empty()
    out = ""
    for c in text:
        out += c
        box.markdown(out)
        time.sleep(0.003)

# --- AUTH ---
if "auth" not in st.session_state:
    st.title("💠 SSGPT INITIALIZE")

    email = st.text_input("Email")
    lang = st.selectbox("Accent", list(lang_map.keys()))

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

st.title("✨ SSGPT ULTRA")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    new_lang = st.selectbox(
        "🎙️ Language",
        list(lang_map.keys()),
        index=list(lang_map.keys()).index(user["lang"])
    )

    if new_lang != user["lang"]:
        user["lang"] = new_lang
        db[st.session_state.email] = user
        save_db(db)
        st.success("Language updated")

# --- CHECK API KEY ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("🚨 Missing GROQ_API_KEY")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- CHAT MEMORY ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- DISPLAY CHAT ---
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
            # Force language
            messages = [
                {
                    "role": "system",
                    "content": f"Reply ONLY in {lang_map[user['lang']]} language."
                }
            ] + st.session_state.chat_history

            # MODEL (UPDATED + SAFE)
            model_name = "mixtral-8x7b-32768"

            res = client.chat.completions.create(
                messages=messages,
                model=model_name,
            )

            ans = res.choices[0].message.content

        except Exception as e:
            ans = f"❌ Error: {str(e)}"

        typewriter(ans)
        trigger_audio(ans, user["lang"])

        st.session_state.chat_history.append(
            {"role": "assistant", "content": ans}
        )
