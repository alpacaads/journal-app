import os
import json
from typing import Any, Dict, List


def _fallback_generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    entry_date = payload["entry_date"]
    mood = payload["mood"]
    answers = payload["answers"]
    media_count = payload.get("media_count", 0)

    went_anywhere = bool(answers.get("went_anywhere", False))
    where = (answers.get("where", "") or "").strip()
    where_activity = (answers.get("where_activity", "") or "").strip()

    memorable = bool(answers.get("memorable", False))
    memorable_text = (answers.get("memorable_text", "") or "").strip()

    challenges = bool(answers.get("challenges", False))
    challenges_text = (answers.get("challenges_text", "") or "").strip()
    handled_text = (answers.get("handled_text", "") or "").strip()

    new_people = bool(answers.get("new_people", False))
    new_people_text = (answers.get("new_people_text", "") or "").strip()

    wins = bool(answers.get("wins", False))
    wins_text = (answers.get("wins_text", "") or "").strip()

    learnings = bool(answers.get("learnings", False))
    learnings_text = (answers.get("learnings_text", "") or "").strip()

    mood_map = {
        "Great": "a really good day",
        "Good": "a solid day",
        "Ok": "a steady day",
        "Hard": "a heavy day",
        "Rough": "a rough one",
    }

    title_bits: List[str] = []
    if went_anywhere and where:
        title_bits.append(where)
    title_bits.append(mood_map.get(mood, "today"))
    title = " • ".join(title_bits[:2]).title()

    paragraphs: List[str] = []

    opener = f"**{entry_date}** felt like {mood_map.get(mood, 'one of those days')}."
    if went_anywhere and where:
        opener += f" I ended up heading to **{where}**."
        if where_activity:
            opener += f" {where_activity}"
        else:
            opener += " It gave the day a bit of shape."
    if media_count:
        opener += f" I captured **{media_count}** moment{'s' if media_count != 1 else ''} along the way."
    paragraphs.append(opener)

    if memorable and memorable_text:
        paragraphs.append(f"The standout moment was: {memorable_text}")

    if new_people and new_people_text:
        paragraphs.append(f"I had a new interaction that stuck with me: {new_people_text}")

    if challenges and challenges_text:
        c = f"One challenge was {challenges_text}"
        if handled_text:
            c += f" — and I handled it by {handled_text}."
        else:
            c += "."
        paragraphs.append(c)

    if wins and wins_text:
        paragraphs.append(f"A win today: {wins_text}")

    if learnings and learnings_text:
        paragraphs.append(f"What I’m taking away from today: {learnings_text}")

    closer = "Even if it wasn’t perfect, it moved the story forward — and that counts."
    if mood in {"Great", "Good"}:
        closer = "It wasn’t a huge day, but it was a
