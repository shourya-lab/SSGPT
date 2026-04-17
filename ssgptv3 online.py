import streamlit as st
import json
import os
from datetime import datetime

# --- UI STYLING (The "Addictive" Look) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(45deg, #00f2ff, #7000ff);
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 15px #00f2ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORY SYSTEM (The "Brain" that stays) ---
USER_DATA_FILE = "user_registry.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f)

# --- APP LOGIC ---
user_db = load_user_data()

# 1. LOGIN / NICKNAME SECTION
if "user_authenticated" not in st.session_state:
    st.title("💠 Welcome to SSGPT Ultra")
    email = st.text_input("Enter Google Email (Simulated for now)")
    nickname = st.text_input("What should the AI call you?")
    
    if st.button("Initialize Consciousness"):
        if email and nickname:
            st.session_state.user_authenticated = email
            st.session_state.nickname = nickname
            
            # If new user, create their profile
            if email not in user_db:
                user_db[email] = {
                    "nickname": nickname,
                    "history": [] # This stores past 3 sessions
                }
                save_user_data(user_db)
            st.rerun()
else:
    # 2. LOAD PREVIOUS CHATS
    current_user = st.session_state.user_authenticated
    nickname = user_db[current_user]["nickname"]
    past_chats = user_db[current_user]["history"]

    st.sidebar.title(f"Welcome back, {nickname}!")
    
    # Show last 3 chat summaries in sidebar
    st.sidebar.subheader("🕒 Past Intel")
    for chat in past_chats[-3:]:
        st.sidebar.info(f"Session: {chat['date']}\n\nLast Topic: {chat['summary']}")

    # 3. CHAT INTERFACE
    st.write(f"### What's our objective today, {nickname}?")
    
    # (Rest of your AI / Graph / Image code goes here)

    # 4. SAVING TO HISTORY (When user finishes)
    if st.button("Archive Session"):
        new_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "summary": "User analyzed stocks and PDFs" # You can make this dynamic
        }
        user_db[current_user]["history"].append(new_entry)
        save_user_data(user_db)
        st.success("Session saved to your profile!")
