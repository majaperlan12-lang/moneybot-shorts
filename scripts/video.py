"""
video.py
--------

Assemble images, audio and subtitles into a vertical video using MoviePy. The
function applies a subtle zoom effect on the background image, overlays
subtitles timed evenly across the audio duration and exports an MP4. A
thumbnail JPEG is also produced from the first frame of the video.
"""

import os
import re
import textwrap
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, vfx


def create_video(image_path: str, audio_path: str, script: str, slug: str, out_dir: str = "out") -> tuple:
    """
    Create a 1080×1920 MP4 video with a background image, voice‑over and timed subtitles.

    Parameters
    ----------
    image_path : str
        Path to the background image.
    audio_path : str
        Path to the audio file.
    script : str
        The narration text to use for subtitles.
    slug : str
        Slug used to name output files.
    out_dir : str
        Directory to save outputs. Created if missing.

    Returns
    -------
    tuple
        A tuple of (video_path, thumbnail_path).
    """
    os.makedirs(out_dir, exist_ok=True)
    # Load audio to determine duration
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    # Prepare the background image clip
    bg = ImageClip(image_path).resize((1080, 1920))
    # Apply a gentle zoom-in effect throughout the video
    video_clip = bg.set_duration(duration).fx(vfx.zoom_in, 0.1)
    # Split script into sentences for subtitle timing
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', script.strip()) if s.strip()]
    num_segments = len(sentences) if sentences else 1
    subclips = []
    for i, sentence in enumerate(sentences):
        start = (i / num_segments) * duration
        end = ((i + 1) / num_segments) * duration
        # Wrap long sentences to fit within the frame width
        wrapped = textwrap.fill(sentence, 40)
        txt_clip = TextClip(
            wrapped,
            fontsize=48,
            color='white',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(1000, None),
            align='center',
        ).set_position(('center', int(1920 * 0.8))).set_start(start).set_end(end)
        subclips.append(txt_clip)
    # Compose video with subtitles and audio
    composite = CompositeVideoClip([video_clip, *subclips])
    composite = composite.set_audio(audio_clip)
    video_path = os.path.join(out_dir, f"{slug}.mp4")
    # Export the video
    composite.write_videofile(video_path, fps=30, codec='libx264', audio_codec='aac', logger=None)
    # Extract a thumbnail
    thumb_path = os.path.join(out_dir, f"{slug}_thumb.jpg")
    composite.save_frame(thumb_path, t=0.0)
    return video_path, thumb_path
