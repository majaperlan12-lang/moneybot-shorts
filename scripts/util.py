import datetime
import re
import unicodedata



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
