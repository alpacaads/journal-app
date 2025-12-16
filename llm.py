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
        closer = "It wasn’t a huge day, but it was a good one — the kind you’re grateful to remember."
    paragraphs.append(closer)

    story_markdown = "\n\n".join(paragraphs)

    highlights = {
        "best_moment": memorable_text or (wins_text if wins else "") or "A quiet moment worth keeping.",
        "hardest_moment": challenges_text or "Nothing major — just normal life friction.",
        "todays_win": wins_text or "Showing up and getting through the day.",
        "lesson": learnings_text or "Small details become the memories.",
    }

    # Theme selection
    theme = "cosy"
    if mood in {"Great", "Good"}:
        theme = "energetic" if went_anywhere else "calm"
    if mood in {"Hard", "Rough"}:
        theme = "calm"

    # Template selection
    if went_anywhere and where and media_count >= 3:
        template = "postcard_map"
    elif media_count >= 4:
        template = "polaroid_trail"
    else:
        template = "minimal_editorial"

    return {
        "title": title,
        "story_markdown": story_markdown,
        "highlights": highlights,
        "theme": theme,
        "template": template,
    }


def generate_journal(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    If OPENAI_API_KEY exists and openai is installed, use it.
    Otherwise use a strong deterministic fallback.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _fallback_generate(payload)

    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI()  # reads OPENAI_API_KEY from env/Streamlit Secrets
    except Exception:
        return _fallback_generate(payload)

    system = (
    "You are a skilled personal journal writer and editor.\n\n"
    "Write in British English.\n"
    "Do NOT invent details.\n"
    "Avoid clichés.\n"
    "Avoid repetition.\n\n"
    "Process:\n"
    "1) Draft a natural narrative like a human reflecting at night (messy is okay).\n"
    "2) Edit it into a refined journal entry and highlights.\n\n"
    "Output must be valid JSON with keys: title, story_markdown, highlights, theme, template.\n\n"
    "Constraints:\n"
    "- title: short, poetic, NOT a full sentence.\n"
    "- story_markdown: 2–5 short paragraphs, vivid and specific.\n"
    "- highlights: concise (max ~12 words each) and MUST NOT repeat sentences from story.\n"
    "- highlights must include: best_moment, hardest_moment, todays_win, lesson.\n"
    "- theme must be one of: calm, energetic, cosy, adventurous.\n"
    "- template must be one of: polaroid_trail, minimal_editorial, postcard_map.\n"
)

    user = {
        "entry_date": payload["entry_date"],
        "mood": payload["mood"],
        "answers": payload["answers"],
        "media_count": payload.get("media_count", 0),
        "note": (
            "Choose a short, clean title (not a full sentence). "
            "Use British English. Don't invent facts. "
            "If media_count is high, choose polaroid_trail. "
            "If went_anywhere is true and a location exists, postcard_map is good."
        ),
    }

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
            ],
        )

        content = resp.choices[0].message.content
        data = json.loads(content)

        for k in ["title", "story_markdown", "highlights", "theme", "template"]:
            if k not in data:
                raise ValueError("Missing key: " + k)

        # Ensure highlights has required keys
        hl = data.get("highlights") or {}
        for hk in ["best_moment", "hardest_moment", "todays_win", "lesson"]:
            hl.setdefault(hk, "")
        data["highlights"] = hl

        return data
    except Exception:
        return _fallback_generate(payload)
