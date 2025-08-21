"""
video.py
--------

Assemble image, audio and (Pillow-rendered) subtitles into a vertical video using MoviePy.
Avoids ImageMagick/TextClip entirely to bypass policy issues on CI runners.
"""

import os
import re
import textwrap
import numpy as np

# Pillow imports
from PIL import Image, ImageDraw, ImageFont

# Pillow 10 removed ANTIALIAS; alias it to LANCZOS if missing
try:
    getattr(Image, "ANTIALIAS")
except AttributeError:
    Image.ANTIALIAS = Image.Resampling.LANCZOS  # type: ignore[attr-defined]

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    vfx,
)

# -------- Pillow subtitle rendering (no ImageMagick) --------

def _load_font(preferred=("DejaVuSans-Bold.ttf", "DejaVuSans.ttf"), size=48):
    # Common path on ubuntu-latest runners
    search_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in search_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                pass
    # Fallback to default (no TTF, metrics less precise)
    return ImageFont.load_default()

def _wrap_text_to_width(draw: ImageDraw.ImageDraw, text: str, font, max_width: int):
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split(" ")
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if draw.textlength(test, font=font) <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
    return lines

def render_subtitle_rgba(
    text: str,
    max_width_px: int = 1000,
    font_size: int = 48,
    padding: int = 20,
    bg_alpha: int = 140,
):
    """Return RGBA numpy array (H, W, 4) with outlined white text on semi-transparent box."""
    font = _load_font(size=font_size)
    # temp image for measurement
    tmp_img = Image.new("RGB", (max_width_px, 10))
    draw = ImageDraw.Draw(tmp_img)
    lines = _wrap_text_to_width(draw, text, font, max_width_px)

    # Measure height
    ascent, descent = font.getmetrics()
    line_h = ascent + descent + 6
    text_h = line_h * max(len(lines), 1)
    text_w = max((int(draw.textlength(line, font=font)) for line in lines), default=0)
    w = max(text_w + padding * 2, max_width_px + padding * 2)
    h = text_h + padding * 2

    # Create RGBA canvas
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background semi-transparent box
    box_w = max(text_w + padding * 2, max_width_px + padding * 2)
    draw.rectangle([0, 0, box_w, h], fill=(0, 0, 0, bg_alpha))

    # Draw outlined text (black stroke)
    y = padding
    for line in lines:
        line_w = int(draw.textlength(line, font=font))
        x = (box_w - line_w) // 2  # center
        # stroke
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            draw.text((x+dx, y+dy), line, font=font, fill=(0,0,0,255))
        # fill
        draw.text((x, y), line, font=font, fill=(255,255,255,255))
        y += line_h

    return np.array(img)  # (H, W, 4)

# -------- Main video assembly --------

def create_video(
    image_path: str,
    audio_path: str,
    script: str,
    slug: str,
    out_dir: str = "out",
) -> tuple[str, str]:
    os.makedirs(out_dir, exist_ok=True)

    # Base background (1080x1920)
    bg_clip = ImageClip(image_path).resize(height=1920).fx(vfx.crop, width=1080, height=1920, x_center=540, y_center=960)
    # subtle zoom
    bg_clip = bg_clip.fx(vfx.resize, lambda t: 1.04 + 0.02 * t)

    # Audio
    narration = AudioFileClip(audio_path)
    duration = min(29.5, narration.duration)  # ≤ 30s
    narration = narration.subclip(0, duration)

    # Split script into sentences
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", script) if s.strip()]
    num_segments = max(len(sentences), 1)

    # Build subtitle overlay clips (Pillow → ImageClip with mask)
    subtitle_clips = []
    for i, sentence in enumerate(sentences):
        start = (i / num_segments) * duration
        end = ((i + 1) / num_segments) * duration

        rgba = render_subtitle_rgba(sentence, max_width_px=1000, font_size=56, padding=24, bg_alpha=120)
        rgb = rgba[..., :3]
        alpha = (rgba[..., 3] / 255.0)

        txt_rgb = ImageClip(rgb).set_start(start).set_end(end).set_position(("center", int(1920 * 0.8)))
        txt_mask = ImageClip(alpha, ismask=True).set_start(start).set_end(end).set_position(("center", int(1920 * 0.8)))
        txt_rgb = txt_rgb.set_mask(txt_mask)
        subtitle_clips.append(txt_rgb)

    clips = [bg_clip] + subtitle_clips

    final = CompositeVideoClip(clips, size=(1080, 1920)).set_duration(duration).set_audio(narration)

    # Export video & thumbnail
    video_path = os.path.join(out_dir, f"{slug}.mp4")
    thumb_path = os.path.join(out_dir, f"{slug}_thumb.jpg")

    final.write_videofile(
        video_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="veryfast",
        threads=2,
        verbose=False,
        logger=None,
    )

    # Thumbnail from first frame
    frame = final.get_frame(0)
    Image.fromarray(frame).save(thumb_path, "JPEG", quality=92)

    final.close()
    narration.close()
    return video_path, thumb_path
