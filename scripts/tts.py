"""
tts.py
------

Generate voice‑overs using OpenAI's text‑to‑speech API. The resulting audio
file is saved to the `out/` directory in WAV format.
"""

import os
import time
import openai



def generate_tts(text: str, slug: str, out_dir: str = "out", voice: str = "alloy", speed: float = 1.0, retries: int = 3) -> str:
    """
    Convert the provided text into speech using OpenAI's TTS API.

    Parameters
    ----------
    text : str
        The script to read aloud.
    slug : str
        Slug used for naming the output file.
    out_dir : str
        Directory where the audio file will be saved.
    voice : str
        Which voice to use. See OpenAI documentation for options.
    speed : float
        Playback speed. 1.0 is normal speed.
    retries : int
        Number of times to retry generation on failure.

    Returns
    -------
    str
        Path to the saved WAV file.
    """
    os.makedirs(out_dir, exist_ok=True)
    for attempt in range(retries):
        try:
            response = openai.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed,
            )
            filepath = os.path.join(out_dir, f"{slug}.wav")
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
