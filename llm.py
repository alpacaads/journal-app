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
        closer = "It wasn’t a huge day, but it was a good one — worth remembering."
    paragraphs.append(closer)

    story_markdown = "\n\n".join(paragraphs)

    highlights = {
        "best_moment": memorable_text if memorable else "",
        "hardest_moment": challenges_text if challenges else "",
        "todays_win": wins_text if wins else "",
        "lesson": learnings_text if learnings else "",
    }

    theme = "calm"
    if mood == "Great":
        theme = "energetic"
    elif mood == "Rough":
        theme = "cosy"

    template = "minimal_editorial"
    if went_anywhere and where:
        template = "postcard_map"
    if media_count >= 3:
        template = "polaroid_trail"

    return {
        "title": title or "Today",
        "story_markdown": story_markdown,
        "highlights": highlights,
        "theme": theme,
        "template": template,
    }


def generate_journal(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a dict:
    {
      "title": str,
      "story_markdown": str,
      "highlights": {...},
      "theme": str,
      "template": str
    }
    Uses OpenAI if OPENAI_API_KEY is present; otherwise falls back to a local generator.
    """
    use_openai = bool(os.getenv("OPENAI_API_KEY"))

    if not use_openai:
        return _fallback_generate(payload)

    themes = ["calm", "energetic", "adventurous", "cosy"]
    templates = ["minimal_editorial", "postcard_map", "polaroid_trail"]

    try:
        from openai import OpenAI

        client = OpenAI()

        system = (
            "You are a thoughtful journaling assistant. "
            "Write a warm, human, first-person journal entry based on the user's day. "
            "Avoid clichés, avoid purple prose. Keep it grounded and specific. "
            "Return STRICT JSON with keys: title, story_markdown, highlights, theme, template."
        )

        user = {
            "instructions": {
                "themes_allowed": themes,
                "templates_allowed": templates,
                "rules": [
                    "Pick a theme from themes_allowed that matches the mood/energy.",
                    "Pick a template from templates_allowed that fits the content.",
                    "highlights keys: best_moment, hardest_moment, todays_win, lesson (any can be empty).",
                    "story_markdown should be 3-6 short paragraphs.",
                    "Keep it authentic and specific to the inputs.",
                ],
            },
            "day": payload,
        }

        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
            ],
            temperature=0.8,
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message.content or "{}"
        data = json.loads(content)

        # Coerce/validate minimal shape
        out = {
            "title": data.get("title") or "Today",
            "story_markdown": data.get("story_markdown") or "",
            "highlights": data.get("highlights") or {},
            "theme": data.get("theme") if data.get("theme") in themes else "calm",
            "template": data.get("template") if data.get("template") in templates else "minimal_editorial",
        }
        if not out["story_markdown"].strip():
            return _fallback_generate(payload)
        return out

    except Exception:
        # Any failure (network, auth, parsing, SDK) → graceful local fallback
        return _fallback_generate(payload)
