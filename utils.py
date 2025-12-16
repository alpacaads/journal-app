import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, Tuple
import hashlib

MEDIA_DIR = Path("data/media")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def today_iso() -> str:
    return date.today().isoformat()

def safe_json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

def safe_json_loads(s: str) -> Any:
    return json.loads(s)

def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "file"

def stable_file_name(original_name: str, content_bytes: bytes) -> str:
    base = slugify(Path(original_name).stem)
    ext = Path(original_name).suffix.lower() or ""
    digest = hashlib.sha256(content_bytes).hexdigest()[:12]
    return f"{base}-{digest}{ext}"

def detect_media_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return "photo"
    if ext in {".mp4", ".mov", ".m4v", ".webm"}:
        return "video"
    # default (treat unknown as photo-ish to avoid breaking)
    return "photo"

def save_upload(original_name: str, content_bytes: bytes) -> Tuple[str, str]:
    """
    Returns (file_path, media_type)
    """
    media_type = detect_media_type(original_name)
    fname = stable_file_name(original_name, content_bytes)
    out_path = MEDIA_DIR / fname
    out_path.write_bytes(content_bytes)
    return str(out_path), media_type
