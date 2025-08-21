"""
content.py
-----------

This module interacts with OpenAI's ChatGPT API to generate scripts, tweets and
metadata for each video. It prompts the model to return a JSON structure with
the following keys: `script`, `tweet`, `title`, `description` and
`hashtags`. A lightweight parser is included to cope with cases where the
response isn't valid JSON.
"""

import os
from openai import OpenAI

client = OpenAI()

def _cta():
    aff = os.environ.get("AFFILIATE_URL", "").strip()
    return f"Support the channel: {aff}" if aff else "Support the channel ❤️"

def _hashes(mode: str):
    base = ["#Shorts", "#Storytime", "#Viral", "#AI"]
    if mode == "voxel_story":
        base += ["#Voxel", "#Gaming", "#MinecraftStyle"]
    elif mode == "spooky_story":
        base += ["#Horror", "#Creepy", "#ScaryStory"]
    elif mode == "funny_texts":
        base += ["#Funny", "#Texts", "#Comedy"]
    return base[:10]

def _system(language: str):
    return f"You are a concise social video writer. Language: {language or 'en'}. Max 30 seconds script. Hook in first 2 seconds."

def _user_prompt(mode: str, seed: str, part: int):
    if mode == "voxel_story":
        return (f"Write a 28-30s narrated micro-episode in English for a voxel/blocky sandbox adventure series titled '{seed}', Part {part}. "
                "1 hero, clear stakes, cliffhanger ending. No trademarked names or logos. Keep sentences short for captions.")
    if mode == "spooky_story":
        return (f"Write a 28-30s creepy micro-horror in English titled '{seed}', Part {part}. "
                "First-person, sensory hooks, safe-for-Shorts, cliffhanger ending.")
    if mode == "funny_texts":
        return (f"Write a 25-30s 'funny texts' skit in English titled '{seed}', Part {part}. "
                "Present as short narrator lines that describe hilarious SMS thread beats. Family-friendly.")
    # mixed fallback
    return f"Write a 28-30s micro-episode in English titled '{seed}', Part {part}. Hook + cliffhanger."

def generate_content(topic, language="en"):
    meta = topic.get("meta", {})
    mode = meta.get("mode", os.environ.get("CONTENT_MODE", "mixed")).lower()
    seed = meta.get("seed", topic.get("title"))
    part = int(meta.get("part", 1))

    messages = [
        {"role": "system", "content": _system(language)},
        {"role": "user", "content": _user_prompt(mode, seed, part)},
    ]
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.8,
    )
    script = resp.choices[0].message.content.strip()

    title = f"{seed} — Part {part}"
    desc = f"{script}\n\n{_cta()}"
    tags = _hashes(mode)
    tweet = f"{title} — {_cta()}"

    return {
        "script": script,
        "title": title,
        "description": desc,
        "hashtags": tags,
        "tweet": tweet[:270],
        "series": {"seed": seed, "part": part, "mode": mode}
    }

