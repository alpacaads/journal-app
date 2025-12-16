import streamlit as st
from datetime import date
from db import init_db

st.set_page_config(
    page_title="Travel Journal",
    page_icon="📓",
    layout="wide",
)

init_db()

st.title("📓 Travel Journal MVP")
st.caption("Capture your day in seconds. Turn it into a beautiful scrapbook-style journal page.")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.metric("Default Entry Date", f"{date.today().isoformat()}")

with col2:
    st.metric("Storage", "SQLite (local)")

with col3:
    st.metric("Rendering", "HTML/CSS templates")

st.markdown("""
### How to use
- Go to **New Entry** → answer a few quick prompts → upload photos/videos → **Generate Journal Page**
- Go to **My Journal** → browse entries → open any entry
- Go to **View Entry** → see the scrapbook page

If you set an `OPENAI_API_KEY`, the writing becomes much more “human”.
Otherwise, the app still generates a nice entry using the fallback writer.
""")
