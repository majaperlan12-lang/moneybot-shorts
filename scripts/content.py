"""
content.py
-----------

This module interacts with OpenAI's ChatGPT API to generate scripts, tweets and
metadata for each video. It prompts the model to return a JSON structure with
the following keys: `script`, `tweet`, `title`, `description` and
`hashtags`. A lightweight parser is included to cope with cases where the
response isn't valid JSON.
"""

import json
import os
import time
import openai


def generate_content(topic: dict, affiliate_url: str = None, retries: int = 3) -> dict:
    """
    Generate narrative content for a short video given a trending topic.

    Parameters
    ----------
    topic : dict
        A dictionary containing `title`, `url` and `snippet` keys describing the topic.
    affiliate_url : str, optional
        A URL to include in calls to action. If not supplied, a generic phrase is used.
    retries : int
        Number of times to retry the API call on transient failures.

    Returns
    -------
    dict
        A dictionary with keys `script`, `tweet`, `title`, `description` and `hashtags`.
    """
    affiliate_text = affiliate_url if affiliate_url else "Support the channel"
    title_topic = topic.get("title", "Unknown topic")
    prompt = (
        f"You are a creative content creator for social media platforms. "
        f"Create the following items for a 30 second vertical video about the topic \"{title_topic}\":\n"
        f"1. SCRIPT: A narrative script in English lasting roughly 30 seconds. Start with a strong hook in the first two seconds. "
        f"Tell a compelling story based on the topic. Conclude with a call-to-action directing viewers to {affiliate_text}.\n"
        f"2. TWEET: A short message under 280 characters in English promoting the video with a call to action to {affiliate_text}.\n"
        f"3. TITLE: A concise, attention grabbing YouTube Short title.\n"
        f"4. DESCRIPTION: A longer description for the video including a call to action directing viewers to {affiliate_text}.\n"
        f"5. HASHTAGS: A list of 6-10 relevant hashtags for the topic.\n"
        f"Format your answer as JSON with the keys script, tweet, title, description, hashtags (the hashtags as a list)."
    )
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            raw = response.choices[0].message.content.strip()
            # Try to parse JSON directly
            try:
                data = json.loads(raw)
                return data
            except json.JSONDecodeError:
                # Attempt to find a JSON substring in the response
                start = raw.find("{")
                end = raw.rfind("}")
                if start != -1 and end != -1 and end > start:
                    try:
                        data = json.loads(raw[start : end + 1])
                        return data
                    except Exception:
                        pass
                # Fallback to manual parsing by labels
                result = {"script": "", "tweet": "", "title": "", "description": "", "hashtags": []}
                for line in raw.splitlines():
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if key.startswith("script"):
                            result["script"] = value
                        elif key.startswith("tweet"):
                            result["tweet"] = value
                        elif key.startswith("title"):
                            result["title"] = value
                        elif key.startswith("description"):
                            result["description"] = value
                        elif key.startswith("hashtags"):
                            tags = [t.strip().lstrip("#") for t in value.replace(",", " ").split()]
                            result["hashtags"] = [f"#{t}" for t in tags if t]
                return result
        except Exception as e:
            # Basic exponential backoff on failure
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    return {}
