import streamlit as st
from gpt4all import GPT4All
import pandas as pd
import plotly.express as px
import requests
import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="SSGPT Multimodal", page_icon="🎨", layout="wide")

# --- VISUALIZER ENGINE ---
def generate_image(prompt):
    """Generates an image using Pollinations AI (Fast & Free)"""
    seed = datetime.datetime.now().microsecond
    url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"
    return url

def create_analysis_graph(data_type, ticker=None):
    """Creates interactive graphs for data analysis"""
    if ticker:
        import yfinance as yf
        df = yf.download(ticker, period="1mo")
        fig = px.line(df, y="Close", title=f"{ticker} 30-Day Analysis", template="plotly_dark")
        fig.update_traces(line_color='#00f2ff')
        return fig
    else:
        # Generic example graph
        df = pd.DataFrame({"Category": ["A", "B", "C"], "Value": [10, 20, 30]})
        return px.bar(df, x="Category", y="Value", template="plotly_dark")

# --- MAIN UI ---
st.markdown('<h1 style="text-align:center; color:#00f2ff;">SSGPT.v3 MULTIMODAL 💠</h1>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask for a stock graph, an image of a cyber-city, or a news report..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. IMAGE GENERATION LOGIC
        if "generate image" in prompt.lower() or "draw" in prompt.lower():
            st.caption("🎨 Rendering AI Visual...")
            img_url = generate_image(prompt)
            st.image(img_url, caption=f"Generated: {prompt}")
            
        # 2. DATA/GRAPH ANALYSIS LOGIC
        elif "graph" in prompt.lower() or "chart" in prompt.lower():
            st.caption("📈 Generating Analytical Data...")
            ticker = "BTC-USD" if "bitcoin" in prompt.lower() else "AAPL"
            fig = create_analysis_graph("line", ticker)
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"Showing latest market trends for {ticker}.")

        # 3. VIDEO REDIRECT LOGIC
        elif "video" in prompt.lower():
            st.caption("🎬 AI Video Synthesis...")
            st.info("Video generation takes 30-60s. Redirecting to Pollinations Video Engine...")
            video_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?model=video"
            st.video(video_url)

        # 4. DEFAULT TEXT RESPONSE
        else:
            st.write("I've analyzed your request. Would you like me to generate a graph or a visual representation of this?")
