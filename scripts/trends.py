"""
trends.py
------------

This module fetches trending topics from public sources without requiring any API keys.
Currently it pulls data from Google News RSS and the Exploding Topics website. Results
are deduplicated and filtered for basic English text. Only the first three topics are returned.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from .util import slugify


def _fetch_google_news(query: str, max_items: int = 5):
    """Fetch a handful of items from Google News RSS for a given search query."""
    url = (
        f"https://news.google.com/rss/search?q={requests.utils.quote(query)}"
        "&hl=en-US&gl=US&ceid=US:en"
    )
    topics = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[: max_items]:
            topics.append(
                {
                    "title": entry.title,
                    "url": entry.link,
                    "snippet": getattr(entry, "summary", ""),
                }
            )
    except Exception:
        pass
    return topics


def _fetch_exploding_topics(max_items: int = 5):
    """Scrape trending topics from the Exploding Topics website as a backup source."""
    topics = []
    try:
        resp = requests.get("https://explodingtopics.com/topics", timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("a", class_="topic-card", limit=max_items)
        for card in cards:
            title_tag = card.find("p", class_="topic-name")
            desc_tag = card.find("p", class_="topic-description")
            if title_tag:
                topics.append(
                    {
                        "title": title_tag.get_text(strip=True),
                        "url": f"https://explodingtopics.com{card.get('href')}",
                        "snippet": desc_tag.get_text(strip=True) if desc_tag else "",
                    }
                )
    except Exception:
        pass
    return topics


def _is_english(text: str) -> bool:
    """
    Very simple heuristic to check if the text contains only ASCII characters. This helps
    avoid non‑English headlines without pulling in heavy language detection libraries.
    """
    try:
        text.encode("ascii")
        return True
    except Exception:
        return False


def get_trends():
    """
    Retrieve up to three trending topics from a mixture of sources.

    The function combines results from several Google News queries and the Exploding Topics
    page, deduplicates them by slugified title and filters out non‑ASCII headlines. The
    first three unique topics are returned as a list of dictionaries with keys `title`,
    `url` and `snippet`.
    """
    queries = ["entertainment", "technology", "business", "fun"]
    topics = []
    # Collect from Google News
    for q in queries:
        topics.extend(_fetch_google_news(q))
        if len(topics) >= 9:
            break
    # Add from Exploding Topics as a fallback
    topics.extend(_fetch_exploding_topics())
    # Deduplicate and filter
    unique = []
    seen_slugs = set()
    for t in topics:
        slug = slugify(t["title"])
        if not slug or slug in seen_slugs:
            continue
        if not _is_english(t["title"]):
            continue
        unique.append(t)
        seen_slugs.add(slug)
        if len(unique) >= 3:
            break
    return unique[:3]
