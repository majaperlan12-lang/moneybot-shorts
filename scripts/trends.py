"""
trends.py
------------

This module fetches trending topics from public sources without requiring any API keys.
Currently it pulls data from Google News RSS and the Exploding Topics website. Results
are deduplicated and filtered for basic English text. Only the first three topics are returned.
"""

import os
from typing import List, Dict
from .util import read_json, write_json, ensure_dir, slugify

STATE_PATH = "state/series.json"

def _default_state():
    return {"series": {}}

def _load_state():
    return read_json(STATE_PATH, _default_state())

def _save_state(state):
    write_json(STATE_PATH, state)

def _series_key(seed: str, mode: str) -> str:
    return f"{mode}:{seed.strip()}"

def _init_series(state, seed: str, mode: str, parts_per: int):
    key = _series_key(seed, mode)
    if key not in state["series"]:
        state["series"][key] = {"seed": seed.strip(), "mode": mode, "next_part": 1, "parts_per_series": parts_per}
    return state

def get_trends() -> List[Dict]:
    """
    Returnerar “teman” med seriesupport.
    Varje item: {title, url, snippet, meta: {series_key, part}}
    """
    mode = os.environ.get("CONTENT_MODE", "mixed").strip().lower()
    parts_per = int(os.environ.get("PARTS_PER_SERIES", "8"))
    seeds_env = os.environ.get("SERIES_SEEDS", "")
    seeds = [s for s in (seeds_env.split(",") if seeds_env else []) if s.strip()]

    # reasonable defaults om inga seeds
    defaults = {
        "voxel_story": ["Nether Portal Mystery", "The Village Heist", "Lost Cave"],
        "spooky_story": ["Whispers in the Attic", "The Night Bus", "Room 313"],
        "funny_texts": ["Awkward Autocorrects", "Group Chat Chaos", "Dad Jokes IRL"],
    }
    if not seeds:
        if mode == "spooky_story":
            seeds = defaults["spooky_story"]
        elif mode == "funny_texts":
            seeds = defaults["funny_texts"]
        elif mode == "voxel_story":
            seeds = defaults["voxel_story"]
        else:
            seeds = defaults["voxel_story"][:1] + defaults["spooky_story"][:1] + defaults["funny_texts"][:1]

    state = _load_state()
    for seed in seeds:
        state = _init_series(state, seed, mode, parts_per)
    _save_state(state)

    # Välj upp till 3 av serierna att producera denna körning
    picks = []
    for seed in seeds:
        key = _series_key(seed, mode)
        s = state["series"][key]
        if s["next_part"] <= s["parts_per_series"]:
            part = s["next_part"]
            title = f"{seed} — Part {part}"
            picks.append({
                "title": title,
                "url": "",
                "snippet": f"{mode} series seed: {seed} (part {part})",
                "meta": {"series_key": key, "seed": seed, "part": part, "mode": mode}
            })
        if len(picks) == 3:
            break

    return picks

def advance_series(series_key: str):
    state = _load_state()
    if series_key in state["series"]:
        state["series"][series_key]["next_part"] += 1
        _save_state(state)
