import datetime
import re
import unicodedata
import os, re, json, time



from pathlib import Path

def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    return re.sub(r"[-\s]+", "-", text)

def safe_filename(name: str) -> str:
    return re.sub(r"[^\w\-\.]", "_", name)

def timestamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def write_json(path: str, data):
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



def slugify(value: str) -> str:
    """
    Simplified slugify function to convert strings into URL‑friendly slugs.
    Non‑ASCII characters are removed and spaces are replaced with hyphens.
    """
    if not isinstance(value, str):
        value = str(value)
    # Normalize unicode and strip accents
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    # Remove invalid characters
    value = re.sub(r'[^a-zA-Z0-9\s-]', '', value).lower()
    # Convert whitespace and hyphens to single hyphens
    value = re.sub(r'[\s-]+', '-', value).strip('-')
    return value



def safe_filename(value: str) -> str:
    """
    Sanitise a string for use as a filename by replacing unsafe characters with underscores.
    """
    if not isinstance(value, str):
        value = str(value)
    return re.sub(r'[^a-zA-Z0-9._-]', '_', value)



def timestamp() -> str:
    """
    Returns a timestamp string in UTC for use in filenames.
    """
    return datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
