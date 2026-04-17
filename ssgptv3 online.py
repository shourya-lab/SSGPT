import streamlit as st
from groq import Groq

st.set_page_config(page_title="SSGPT DEBUG", layout="centered")

st.title("🔍 SSGPT DEBUG MODE")

# --- DEBUG: SHOW SECRETS ---
st.subheader("🔑 Debug: Secrets Check")

if len(st.secrets) == 0:
    st.error("❌ No secrets found at all")
else:
    st.success("✅ Secrets loaded")
    st.write(st.secrets)

# --- HARD FAIL IF KEY MISSING ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("🚨 GROQ_API_KEY NOT FOUND")
    st.stop()

st.success("✅ GROQ_API_KEY detected")

# --- CHAT INPUT ---
prompt = st.text_input("Ask something")

if prompt:
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )

        ans = res.choices[0].message.content
        st.success("✅ AI Response:")
        st.write(ans)

    except Exception as e:
        st.error("❌ ERROR OCCURRED")
        st.write(str(e))
