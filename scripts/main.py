"""
main.py
-------

Entry point for the Moneybot Shorts pipeline. This module orchestrates
retrieving trending topics, generating content, producing media assets,
posting to Bluesky and uploading to YouTube. Errors are logged and the
pipeline continues with the next topic.
"""

import os
import traceback

from .trends import get_trends
from .content import generate_content
from .images import generate_image_for_topic
from .tts import generate_tts
from .video import create_video
from .bluesky import post_bluesky
from .youtube_uploader import upload_youtube
from .util import slugify, timestamp


def main():
    affiliate_url = os.environ.get("AFFILIATE_URL")
    topics = get_trends()
    if not topics:
        print("No trends found")
        return
    for topic in topics:
        try:
            print(f"Processing topic: {topic['title']}")
            # Generate narrative content and metadata
            content = generate_content(topic, affiliate_url)
            script = content.get("script", "")
            tweet = content.get("tweet", "")
            title = content.get("title", topic['title'])
            description = content.get("description", "")
            hashtags = content.get("hashtags", [])
            # Create unique slug based on title and timestamp to avoid collisions
            slug = f"{slugify(title)}-{timestamp()}"
            # Generate background image
            img_path = generate_image_for_topic(topic['title'], slug)
            # Generate voice over audio
            audio_path = generate_tts(script, slug)
            # Compose video and thumbnail
            video_path, thumb_path = create_video(img_path, audio_path, script, slug)
            # Post to Bluesky if possible
            if tweet:
                post_bluesky(tweet, thumb_path, affiliate_url)
            # Upload to YouTube (optional)
            upload_youtube(video_path, title, description + "\n\n" + (affiliate_url or ""), hashtags)
        except Exception as e:
            print(f"Error processing topic {topic['title']}: {e}")
            traceback.print_exc()
            continue


if __name__ == "__main__":
    main()
