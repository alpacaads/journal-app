import os
from typing import Any, Dict, List, Optional

def _fallback_generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    entry_date = payload["entry_date"]
    mood = payload["mood"]
    answers = payload["answers"]
    media_count = payload.get("media_count", 0)

    went_anywhere = answers.get("went_anywhere", False)
    where = answers.get("where", "").strip()

    memorable = answers.get("memorable", False)
    memorable_text = answers.get("memorable_text", "").strip()

    challenges = answers.get("challenges", False)
    challenges_text = answers.get("challenges_text", "").strip()
    handled_text = answers.get("handled_text", "").strip()

    new_people = answers.get("new_people", False)
    new_people_text = answers.get("new_people_text", "").strip()

    wins = answers.get("wins", False)
    wins_text = answers.get("wins_text", "").strip()

    learnings = answers.get("learnings", False)
    learnings_text = answers.get("learnings_text", "").strip()

    title_bits = []
    if went_anywhere and where:
        title_bits.append(where)
    mood_map = {"Great": "a really good day", "Good": "a solid day", "Ok": "a steady day", "Hard": "a heavy day", "Rough": "a rough one"}
    title_bits.append(mood_map.get(mood, "today"))
    title = " • ".join(title_bits[:2]).title()

    paragraphs: List[str] = []
    opener = f"**{entry_date}** felt like {mood_map.get(mood, 'one of those days')}."
    if went_anywhere and where:
        opener += f" I ended up heading to **{where}**, which gave the day a bit of shape."
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
        "You are a gifted travel-journal editor and scrapbook storyteller. "
        "Write in British English. Keep it vivid, warm, and specific. "
        "Avoid cliché. Do not invent facts not provided. "
        "Output must be valid JSON with keys: title, story_markdown, highlights, theme, template. "
        "highlights must include: best_moment, hardest_moment, todays_win, lesson. "
        "theme must be one of: calm, energetic, cosy, adventurous. "
        "template must be one of: polaroid_trail, minimal_editorial, postcard_map."
    )

    user = {
        "entry_date": payload["entry_date"],
        "mood": payload["mood"],
        "answers": payload["answers"],
        "media_count": payload.get("media_count", 0),
        "note": "If media_count is high, choose polaroid_trail. If location exists and went_anywhere is true, postcard_map is good.",
    }

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": str(user)},
            ],
        )
        import json
        content = resp.choices[0].message.content
        data = json.loads(content)

        for k in ["title", "story_markdown", "highlights", "theme", "template"]:
            if k not in data:
                raise ValueError("Missing key: " + k)
        return data
    except Exception:
        return _fallback_generate(payload)

    client = OpenAI()

    system = (
        "You are a gifted travel-journal editor and scrapbook storyteller. "
        "Write in British English. Keep it vivid, warm, and specific. "
        "Avoid cliché. Do not invent facts not provided. "
        "Output must be valid JSON with keys: title, story_markdown, highlights, theme, template. "
        "highlights must include: best_moment, hardest_moment, todays_win, lesson. "
        "theme must be one of: calm, energetic, cosy, adventurous. "
        "template must be one of: polaroid_trail, minimal_editorial, postcard_map."
    )

    user = {
        "entry_date": payload["entry_date"],
        "mood": payload["mood"],
        "answers": payload["answers"],
        "media_count": payload.get("media_count", 0),
        "note": "If media_count is high, choose polaroid_trail. If location exists and went_anywhere is true, postcard_map is good.",
    }

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.7,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": str(user)},
        ],
    )

    import json
    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
        # Minimal validation & safe defaults
        for k in ["title", "story_markdown", "highlights", "theme", "template"]:
            if k not in data:
                raise ValueError("Missing key: " + k)
        return data
    except Exception:
        return _fallback_generate(payload)
