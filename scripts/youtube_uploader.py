"""
youtube_uploader.py
-------------------

Upload generated videos to YouTube Shorts using OAuth credentials. If the
required environment variables (`YT_CLIENT_ID`, `YT_CLIENT_SECRET` and
`YT_REFRESH_TOKEN`) are missing, the upload step is skipped and the
function returns the string "skipped". Errors during upload are logged but
do not halt the main pipeline.
"""

import os
from typing import List, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_youtube(video_path: str, title: str, description: str, tags: List[str]) -> Optional[dict]:
    """
    Upload a video to YouTube as a public Short.

    Parameters
    ----------
    video_path : str
        Path to the MP4 file to upload.
    title : str
        Video title.
    description : str
        Video description.
    tags : list of str
        List of hashtags or keywords.

    Returns
    -------
    dict or None
        The API response if uploaded successfully, or "skipped" if credentials are missing, or None on error.
    """
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")
    if not (client_id and client_secret and refresh_token):
        print("Skipping YouTube upload, saved to out/")
        return "skipped"
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    try:
        creds.refresh(Request())
        youtube = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22",  # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        return response
    except Exception as e:
        print(f"YouTube upload error: {e}")
        return None
