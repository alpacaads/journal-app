import streamlit as st
from datetime import date
from db import upsert_entry, add_media
from utils import today_iso, safe_json_dumps, save_upload
from llm import generate_journal

st.set_page_config(page_title="New Entry", page_icon="➕", layout="wide")

USER_ID = "demo"  # MVP user

st.title("➕ New Entry")

# Date default = today, user can change it
entry_date = st.date_input(
    "Entry date",
    value=date.fromisoformat(today_iso()),
    help="Defaults to today. Change this to backfill a missed day.",
)

st.caption("Tip: keep it quick. Most questions are Yes/No — only the relevant follow-ups appear.")

mood = st.selectbox("How was today?", ["Great", "Good", "Ok", "Hard", "Rough"], index=1)

st.divider()

colA, colB = st.columns([1, 1])

with colA:
    went_anywhere = st.toggle("Did you go anywhere today?", value=False)
    where = ""
    if went_anywhere:
        where = st.text_input("Where did you go?", placeholder="e.g., South Bank, Noosa, Mum’s place")

    memorable = st.toggle("Did you do something memorable?", value=False)
    memorable_text = ""
    if memorable:
        memorable_text = st.text_area("What happened?", height=80, placeholder="1–2 sentences is plenty.")

    new_people = st.toggle("Did you meet or talk to someone new?", value=False)
    new_people_text = ""
    if new_people:
        new_people_text = st.text_area("What was the interaction?", height=80, placeholder="Quick summary is fine.")

with colB:
    challenges = st.toggle("Any challenges today?", value=False)
    challenges_text = ""
    handled_text = ""
    if challenges:
        challenges_text = st.text_area("What was tough?", height=80, placeholder="What made it hard?")
        handled_text = st.text_area("How did you handle it? (optional)", height=80, placeholder="What did you do next?")

    wins = st.toggle("Any wins or progress?", value=False)
    wins_text = ""
    if wins:
        wins_text = st.text_area("What went well?", height=80, placeholder="Something you’re glad happened.")

    learnings = st.toggle("Any learnings today?", value=False)
    learnings_text = ""
    if learnings:
        learnings_text = st.text_area("What did you learn?", height=80, placeholder="A thought worth keeping.")

st.divider()

st.subheader("Media")
st.write("Upload photos/videos (optional). The generator will weave them into the page.")

uploads = st.file_uploader(
    "Add files",
    type=["jpg", "jpeg", "png", "webp", "gif", "mp4", "mov", "m4v", "webm"],
    accept_multiple_files=True,
)

answers = {
    "went_anywhere": went_anywhere,
    "where": where,
    "memorable": memorable,
    "memorable_text": memorable_text,
    "challenges": challenges,
    "challenges_text": challenges_text,
    "handled_text": handled_text,
    "new_people": new_people,
    "new_people_text": new_people_text,
    "wins": wins,
    "wins_text": wins_text,
    "learnings": learnings,
    "learnings_text": learnings_text,
}

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    save_draft = st.button("Save draft", use_container_width=True)

with col2:
    generate = st.button("Generate journal page", type="primary", use_container_width=True)

with col3:
    st.info("You can generate even with zero uploads. Add media later and regenerate.", icon="ℹ️")

entry_date_iso = entry_date.isoformat()

if save_draft:
    entry_id = upsert_entry(
        user_id=USER_ID,
        entry_date=entry_date_iso,
        mood=mood,
        answers_json=safe_json_dumps(answers),
        status="draft",
        generated_json=None,
    )
    # Save media (if any) even for draft
    if uploads:
        for f in uploads:
            content = f.getvalue()
            file_path, media_type = save_upload(f.name, content)
            add_media(entry_id, media_type, file_path, f.name)
    st.success(f"Saved draft for {entry_date_iso}.")
    st.session_state["view_entry_id"] = entry_id
    st.switch_page("pages/3_View_Entry.py")

if generate:
    entry_id = upsert_entry(
        user_id=USER_ID,
        entry_date=entry_date_iso,
        mood=mood,
        answers_json=safe_json_dumps(answers),
        status="complete",
        generated_json=None,
    )

    media_count = 0
    if uploads:
        for f in uploads:
            content = f.getvalue()
            file_path, media_type = save_upload(f.name, content)
            add_media(entry_id, media_type, file_path, f.name)
            media_count += 1

    payload = {
        "entry_date": entry_date_iso,
        "mood": mood,
        "answers": answers,
        "media_count": media_count,
    }

    generated = generate_journal(payload)

    upsert_entry(
        user_id=USER_ID,
        entry_date=entry_date_iso,
        mood=mood,
        answers_json=safe_json_dumps(answers),
        status="generated",
        generated_json=safe_json_dumps(generated),
    )

    st.success("Generated your journal page.")
    st.session_state["view_entry_id"] = entry_id
    st.switch_page("pages/3_View_Entry.py")
