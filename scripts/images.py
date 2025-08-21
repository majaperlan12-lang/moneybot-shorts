"""
images.py
---------

Generate vertical background images using OpenAI's DALL·E model. The function
constructs an evocative prompt based on the topic title and downloads the
returned image. Images are saved to the `out/` directory.
"""

import os
from openai import OpenAI
from .util import ensure_dir, safe_filename

client = OpenAI()

def _img_prompt(mode: str, seed: str, part: int):
    if mode == "voxel_story":
        return (f"Vertical 1080x1920 digital art in a voxel/blocky sandbox style (no logos), dramatic lighting, "
                f"scene that fits the theme '{seed}', episode Part {part}. High contrast, cinematic, clean focal point.")
    if mode == "spooky_story":
        return (f"Vertical 1080x1920 eerie cinematic illustration, moody lighting, subtle horror (no gore), "
                f"fits theme '{seed}', Part {part}.")
    if mode == "funny_texts":
        return (f"Vertical 1080x1920 clean minimal background suitable for overlay text, playful vibe, "
                f"fits theme '{seed}', Part {part}.")
    return "Vertical 1080x1920 cinematic illustration, dramatic, clean focal point."

def generate_image_for_topic(topic, out_dir="out"):
    meta = topic.get("meta", {})
    mode = meta.get("mode", os.environ.get("CONTENT_MODE", "mixed")).lower()
    seed = meta.get("seed", topic.get("title"))
    part = int(meta.get("part", 1))

    prompt = _img_prompt(mode, seed, part)
    ensure_dir(out_dir)

    slug = safe_filename(f"{seed}-part-{part}".lower())
    out_path = os.path.join(out_dir, f"{slug}.jpg")

    img = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1080x1920",
    )
    b64 = img.data[0].b64_json
    import base64
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(b64))
    return out_path, slug
