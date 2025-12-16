import streamlit as st
import markdown as md  # Streamlit bundles markdown rendering internally, but we want HTML conversion
from db import get_entry, list_media
from utils import safe_json_loads
from renderers import render_entry_html

st.set_page_config(page_title="View Entry", page_icon="🖼️", layout="wide")

st.title("🖼️ Entry")

entry_id = st.session_state.get("view_entry_id", None)

if entry_id is None:
    st.info("Open an entry from **My Journal** or generate one from **New Entry**.")
    st.stop()

entry = get_entry(int(entry_id))
if not entry:
    st.error("Entry not found.")
    st.stop()

media_items = list_media(int(entry_id))
answers = safe_json_loads(entry["answers_json"])
generated = safe_json_loads(entry["generated_json"]) if entry.get("generated_json") else None

left, right = st.columns([0.35, 0.65])

with left:
    st.subheader("Details")
    st.write(f"**Date:** {entry['entry_date']}")
    st.write(f"**Mood:** {entry['mood']}")
    st.write(f"**Status:** {entry['status']}")

    st.subheader("Captured answers")
    st.json(answers)

    st.subheader("Media")
    if not media_items:
        st.caption("No media added yet.")
    else:
        for m in media_items:
            st.caption(f"{m['media_type'].upper()}: {m['original_name']}")
            if m["media_type"] == "video":
                st.video(m["file_path"])
            else:
                st.image(m["file_path"], use_column_width=True)

with right:
    st.subheader("Scrapbook Page")

    if not generated:
        st.warning("This entry hasn’t been generated yet. Go to **New Entry** and click Generate.")
        st.stop()

    title = generated.get("title", "Untitled")
    story_md = generated.get("story_markdown", "")
    highlights = generated.get("highlights", {}) or {}
    theme = generated.get("theme", "calm")
    template = generated.get("template", "minimal_editorial")

    # Convert markdown to HTML
    story_html = md.markdown(story_md, extensions=["extra", "sane_lists"])

    location = answers.get("where", "") if answers.get("went_anywhere") else ""

    html = render_entry_html(
        entry_date=entry["entry_date"],
        mood=entry["mood"],
        title=title,
        story_html=story_html,
        highlights=highlights,
        theme=theme,
        template=template,
        media_items=media_items,
        location=location,
    )

    st.components.v1.html(html, height=900, scrolling=True)
