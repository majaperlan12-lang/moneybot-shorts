"""
images.py
---------

Generate vertical background images using OpenAI's DALL·E model. The function
constructs an evocative prompt based on the topic title and downloads the
returned image. Images are saved to the `out/` directory.
"""

import os
import time
import requests
import openai


def generate_image_for_topic(topic_title: str, slug: str, out_dir: str = "out", retries: int = 3) -> str:
    """
    Generate a dramatic, vertical digital artwork representing the given topic.

    Parameters
    ----------
    topic_title : str
        The title of the topic to visualise.
    slug : str
        Slugified string used to name the output file.
    out_dir : str
        Directory where the output image will be saved. Created if it doesn't exist.
    retries : int
        Number of times to retry generation on failure.

    Returns
    -------
    str
        Path to the saved JPEG image.
    """
    prompt = f"digital art, dramatic, vertical composition illustrating {topic_title}, 1080x1920"
    os.makedirs(out_dir, exist_ok=True)
    for attempt in range(retries):
        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1792",
                response_format="url",
            )
            image_url = response.data[0].url
            r = requests.get(image_url, timeout=60)
            r.raise_for_status()
            path = os.path.join(out_dir, f"{slug}.jpg")
            with open(path, "wb") as f:
                f.write(r.content)
            return path
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
