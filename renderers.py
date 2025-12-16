from typing import Any, Dict, List
from html import escape

def _css_base() -> str:
    return """
    <style>
      .page { max-width: 980px; margin: 0 auto; padding: 28px; border-radius: 18px; color: #101010; }
      .title { font-size: 34px; font-weight: 750; margin: 0 0 6px 0; letter-spacing: -0.02em; }
      .meta { opacity: 0.75; margin-bottom: 18px; }
      .grid { display: grid; gap: 18px; }
      .two { grid-template-columns: 1.1fr 0.9fr; }
      .story { font-size: 16.5px; line-height: 1.6; }
      .chips { display:flex; flex-wrap: wrap; gap: 10px; margin: 18px 0 10px; }
      .chip { padding: 8px 12px; border-radius: 999px; font-size: 13px; background: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.08); }
      .media-strip { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
      .frame { border-radius: 14px; overflow: hidden; background: rgba(255,255,255,0.8); border: 1px solid rgba(0,0,0,0.08); box-shadow: 0 10px 22px rgba(0,0,0,0.06); }
      .frame img { width: 100%; display:block; }
      .frame video { width: 100%; display:block; }
      .polaroid { padding: 12px; }
      .caption { padding: 10px 12px 14px; font-size: 13px; opacity: 0.85; }
      .section-title { font-weight: 700; margin: 12px 0 6px; }
      .card { padding: 14px 16px; border-radius: 14px; background: rgba(255,255,255,0.72); border: 1px solid rgba(0,0,0,0.08); }
      .mapcard { display:flex; flex-direction: column; gap: 8px; }
      .mapbadge { display:inline-block; font-size: 12px; padding: 6px 10px; border-radius: 999px; background: rgba(0,0,0,0.06); width: fit-content; }
      a { color: inherit; }
      @media (max-width: 900px) {
        .two { grid-template-columns: 1fr; }
        .media-strip { grid-template-columns: 1fr; }
      }
    </style>
    """

def _bg_for_theme(theme: str) -> str:
    # No hard-coded colours requested by user; these are subtle defaults for MVP.
    # If you want “brand-able” themes later, we can move these into editable settings.
    if theme == "energetic":
        return "background: linear-gradient(135deg, #fff6e5 0%, #eef7ff 100%);"
    if theme == "adventurous":
        return "background: linear-gradient(135deg, #ecfff3 0%, #fff0f3 100%);"
    if theme == "cosy":
        return "background: linear-gradient(135deg, #fff3f0 0%, #f3f0ff 100%);"
    return "background: linear-gradient(135deg, #f2f7ff 0%, #f7fff6 100%);"  # calm

def render_entry_html(
    entry_date: str,
    mood: str,
    title: str,
    story_html: str,
    highlights: Dict[str, str],
    theme: str,
    template: str,
    media_items: List[Dict[str, Any]],
    location: str = "",
) -> str:
    css = _css_base()
    bg = _bg_for_theme(theme)

    chips = []
    for label, value in [
        ("Best moment", highlights.get("best_moment", "")),
        ("Hardest moment", highlights.get("hardest_moment", "")),
        ("Today’s win", highlights.get("todays_win", "")),
        ("Lesson", highlights.get("lesson", "")),
    ]:
        if value.strip():
            chips.append(f'<div class="chip"><strong>{escape(label)}:</strong> {escape(value.strip())}</div>')
    chips_html = f'<div class="chips">{"".join(chips)}</div>' if chips else ""

    def media_block(items: List[Dict[str, Any]], polaroid: bool = False) -> str:
        blocks = []
        for m in items:
            path = m["file_path"]
            mt = m["media_type"]
            name = m.get("original_name", "")
            caption = escape(name) if name else ""
            if mt == "video":
                inner = f'<video controls muted playsinline src="{escape(path)}"></video>'
            else:
                inner = f'<img src="{escape(path)}" alt="{escape(name)}"/>'

            if polaroid:
                blocks.append(
                    f'<div class="frame polaroid">{inner}<div class="caption">{caption}</div></div>'
                )
            else:
                blocks.append(f'<div class="frame">{inner}</div>')
        return f'<div class="media-strip">{"".join(blocks)}</div>' if blocks else ""

    media_html = ""
    if template == "polaroid_trail":
        media_html = media_block(media_items[:8], polaroid=True)
        layout = f"""
          <div class="grid two">
            <div>
              <div class="title">{escape(title)}</div>
              <div class="meta">{escape(entry_date)} · Mood: {escape(mood)}</div>
              {chips_html}
              <div class="card story">{story_html}</div>
            </div>
            <div>
              <div class="section-title">Moments</div>
              {media_html}
            </div>
          </div>
        """
    elif template == "postcard_map":
        media_html = media_block(media_items[:6], polaroid=False)
        loc = location.strip()
        map_card = ""
        if loc:
            map_card = f"""
            <div class="card mapcard">
              <div class="mapbadge">📍 Location</div>
              <div style="font-size:18px; font-weight:750;">{escape(loc)}</div>
              <div style="opacity:0.75;">Add maps later (MVP). This is the “postcard” anchor.</div>
            </div>
            """
        layout = f"""
          <div class="title">{escape(title)}</div>
          <div class="meta">{escape(entry_date)} · Mood: {escape(mood)}</div>
          {chips_html}
          <div class="grid two">
            <div class="card story">{story_html}</div>
            <div>
              {map_card}
              <div class="section-title" style="margin-top:14px;">Gallery</div>
              {media_html}
            </div>
          </div>
        """
    else:  # minimal_editorial
        hero = media_items[:1]
        rest = media_items[1:5]
        hero_html = media_block(hero, polaroid=False) if hero else ""
        rest_html = media_block(rest, polaroid=False) if rest else ""
        layout = f"""
          <div class="title">{escape(title)}</div>
          <div class="meta">{escape(entry_date)} · Mood: {escape(mood)}</div>
          {chips_html}
          {hero_html}
          <div class="grid">
            <div class="card story">{story_html}</div>
            {rest_html}
          </div>
        """

    return f"""
    {css}
    <div class="page" style="{bg}">
      {layout}
      <div style="opacity:0.6; font-size:12px; margin-top:18px;">
        Generated scrapbook page · Template: {escape(template)} · Theme: {escape(theme)}
      </div>
    </div>
    """
