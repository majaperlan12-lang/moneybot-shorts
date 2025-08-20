"""
bluesky.py
-----------

This module handles posting content to Bluesky. Posting only occurs if the
environment variables `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD` are
present. A thumbnail image can optionally be uploaded and attached to the
post. Errors are logged but do not halt the main pipeline.
"""

import os
from atproto import Client


def post_bluesky(text: str, image_path: str = None, url: str = None) -> None:
    """
    Post a message to Bluesky with an optional image and link.

    Parameters
    ----------
    text : str
        The main body of the post.
    image_path : str, optional
        Path to an image file to upload. Must be JPEG.
    url : str, optional
        A URL to append to the post text.
    """
    handle = os.environ.get("BLUESKY_HANDLE")
    password = os.environ.get("BLUESKY_APP_PASSWORD")
    if not handle or not password:
        print("Bluesky credentials missing, skipping post")
        return
    client = Client()
    try:
        client.login(handle, password)
        full_text = text.strip()
        if url:
            full_text = f"{full_text} {url.strip()}"
        embed = None
        if image_path and os.path.isfile(image_path):
            with open(image_path, "rb") as f:
                upload_resp = client.com.atproto.repo.upload_blob(f, "image/jpeg")
            embed = {"images": [{"image": upload_resp.blob, "alt": "thumbnail"}]}
        client.com.atproto.repo.create_record(
            repo=client.did,
            collection="app.bsky.feed.post",
            record={
                "$type": "app.bsky.feed.post",
                "text": full_text,
                "createdAt": client.com.atproto.repo.get_current_time(),
                "embed": embed,
            },
        )
    except Exception as e:
        print(f"Bluesky error: {e}")
