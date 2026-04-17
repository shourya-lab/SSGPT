# --- 1. REWARD VALIDATION LOGIC ---
# This ensures they actually describe a problem or feedback as you requested
def validate_review(text):
    # Check for length and keywords to ensure it's a "decent" review
    keywords = ["problem", "improve", "feature", "fix", "good", "better", "suggest"]
    has_keywords = any(word in text.lower() for word in keywords)
    return len(text) > 60 and has_keywords

# --- 2. THE ADDICTIVE "OBSIDIAN GOLD" UI ---
def apply_pro_skin():
    st.markdown("""
        <style>
        /* Deep Obsidian Background with Gold Neon Glow */
        .stApp {
            background: radial-gradient(circle, #1a1a1a 0%, #000000 100%);
            color: #FFFFFF;
        }
        /* Glowing Gold Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #FFD700, #B8860B);
            color: black !important;
            border: none;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
            transition: 0.3s;
            font-weight: 900;
        }
        .stButton>button:hover {
            box-shadow: 0 0 40px rgba(255, 215, 0, 0.9);
            transform: scale(1.02);
        }
        /* Gold Input Border */
        .stChatInput {
            border: 2px solid #FFD700 !important;
            box-shadow: 0 0 10px #FFD700;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. THE REWARD INTERFACE ---
with st.sidebar:
    if not user_profile["pro"]:
        st.markdown("### 🎁 UNLOCK SPECIAL REWARDS")
        st.write("Submit a decent review (mention a problem or fix) on Product Hunt to unlock.")
        review_input = st.text_area("Paste your review link or text here:", placeholder="I found a problem with...")
        
        if st.button("VERIFY & UPGRADE"):
            if validate_review(review_input):
                user_profile["pro"] = True
                db[st.session_state.email]["pro"] = True
                save_db(db)
                st.balloons()
                st.success("OBSIDIAN GOLD UNLOCKED! Refreshing systems...")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Review must be at least 60 characters and provide actual feedback/problems.")
