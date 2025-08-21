"""
main.py
-------

Entry point for the Moneybot Shorts pipeline.
Generates themed series videos (e.g. voxel stories, spooky stories, funny texts).
Each run produces up to 3 new parts. Continues series state automatically.
"""

import os
import traceback

from .trends import get_trends, advance_series
from .content import generate_content
from .images import generate_image_for_topic
from .tts import generate_tts
from .video import create_video
from .bluesky import post_bluesky
from .youtube_uploader import upload_youtube
from .util import slugify, timestamp, ensure_dir


def main():
    language = os.environ.get("LANGUAGE", "en")
    affiliate_url = os.environ.get("AFFILIATE_URL")
    ensure_dir("out")

    topics = get_trends()
    if not topics:
        print("No topics found")
        return

    produced = 0
    for topic in topics:
        try:
            print(f"Processing topic: {topic['title']}")
            # Generate narrative content and metadata
            content = generate_content(topic, language=language)
            script = content.get("script", "")
            tweet = content.get("tweet", "")
            title = content.get("title", topic['title'])
            description = content.get("description", "")
            hashtags = content.get("hashtags", [])
            slug = slugify(title)

            # Generate background image
            img_path, slug = generate_image_for_topic(topic)
            # Generate voice over audio
            audio_path = generate_tts(script, slug)
            # Compose video and thumbnail
            video_path, thumb_path = create_video(img_path, audio_path, script, slug)

            # Post to Bluesky if possible
            if tweet:
                post_bluesky(tweet, thumb_path, affiliate_url)
            # Upload to YouTube (optional)
            upload_youtube(video_path, title, description + "\n\n" + (affiliate_url or ""), hashtags)

            # advance to next part in this series
            series_key = topic["meta"]["series_key"]
            advance_series(series_key)

            produced += 1
        except Exception as e:
            print(f"Error processing topic {topic.get('title')}: {e}")
            traceback.print_exc()
            continue

    print(f"Produced {produced} videos.")


if __name__ == "__main__":
    main()
