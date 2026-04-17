import streamlit as st
import streamlit.components.v1 as components
import base64
import time

# --- 1. THE SOUND ENGINE ---
def play_sound(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# --- 2. THE "HEY SSGPT" LISTENER (JavaScript) ---
# Note: This uses the Browser's WebSpeech API
components.html("""
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
        if (transcript.includes("hey ssgpt")) {
            window.parent.postMessage({type: 'ssgpt_activate', text: transcript}, "*");
        }
    };
    recognition.start();
    </script>
    """, height=0)

# --- 3. ADDICTIVE UI STYLING ---
st.markdown("""
    <style>
    /* Typewriter Animation */
    .typewriter h1 {
      overflow: hidden;
      border-right: .15em solid orange;
      white-space: nowrap;
      margin: 0 auto;
      letter-spacing: .15em;
      animation: typing 3.5s steps(40, end), blink-caret .75s step-end infinite;
    }
    @keyframes typing { from { width: 0 } to { width: 100% } }
    @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: orange; } }
    
    /* Neon Glow Buttons */
    .stButton>button {
        box-shadow: 0 0 10px #00f2ff, 0 0 20px #7000ff;
        border: 2px solid #00f2ff !format;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. THE CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💠 SSGPT ULTRA: VOICE ACTIVE")

# Simulate a sound on start
if st.button("🔊 Test Audio Systems"):
    # You would replace "ping.mp3" with your actual sound file path
    play_sound("ping.mp3") 

if prompt := st.chat_input("Listening for 'Hey SSGPT'..."):
    # Play 'Processing' Sound
    # play_sound("processing.mp3")
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = "I am processing your command, SHOURYA. Global intel synchronized."
        
        # TYPEWRITER EFFECT
        curr_text = ""
        for char in full_response:
            curr_text += char
            message_placeholder.markdown(curr_text + "▌")
            time.sleep(0.03)
        message_placeholder.markdown(full_response)
        
        # play_sound("success.mp3")
