import streamlit as st
from db import list_entries

st.set_page_config(page_title="My Journal", page_icon="📚", layout="wide")

USER_ID = "demo"  # MVP user

st.title("📚 My Journal")
rows = list_entries(USER_ID)

if not rows:
    st.info("No entries yet. Go to **New Entry** to create one.")
    st.stop()

# Simple table-like list
for (entry_id, entry_date, mood, status, updated_at) in rows:
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
        c1.markdown(f"**{entry_date}**")
        c2.write(f"Mood: {mood}")
        c3.write(f"Status: {status}")
        c4.write(f"Updated: {updated_at}")

        if st.button("Open", key=f"open_{entry_id}"):
            st.session_state["view_entry_id"] = entry_id
            st.switch_page("pages/3_View_Entry.py")
