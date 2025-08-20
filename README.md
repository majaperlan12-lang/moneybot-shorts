# Moneybot Shorts

This repository contains an automated bot that generates short‑form vertical videos (1080×1920) about trending topics three times per day. The pipeline fetches trending topics from open sources, writes a concise script with a strong hook, generates a custom background image and voice‑over using OpenAI, composes the final video with subtitles, and publishes it to Bluesky and optionally to YouTube Shorts. Each video includes a call‑to‑action to support the channel via an affiliate link if provided.

## Requirements

* Python 3.11+
* An OpenAI API key set in the `OPENAI_API_KEY` secret.
* FFmpeg installed (automatically installed in GitHub Actions).
* Optional: Bluesky handle and app password for posting.
* Optional: YouTube OAuth client ID, client secret and refresh token to upload videos automatically.
* Optional: An affiliate URL stored as a secret `AFFILIATE_URL` for monetisation.

## Repository structure

```
moneybot-shorts/
├── .github/workflows/run.yml   # GitHub Actions workflow that runs 3 times per day
├── scripts/
│   ├── requirements.txt        # Python dependencies
│   ├── util.py                 # Helper functions (slugify, filenames, timestamps)
│   ├── trends.py               # Fetch trending topics from public sources
│   ├── content.py              # Generate script, tweet, title, description and hashtags using OpenAI
│   ├── images.py               # Generate background images via OpenAI Images
│   ├── tts.py                  # Generate voice‑overs using OpenAI TTS
│   ├── video.py                # Assemble images, audio and subtitles into a video
│   ├── bluesky.py              # Post to Bluesky if credentials are provided
│   ├── youtube_uploader.py     # Upload to YouTube Shorts if OAuth credentials are provided
│   └── main.py                 # Main entry point coordinating the pipeline
├── out/                        # Rendered MP4 videos and thumbnails are saved here
├── README.md                   # This file
└── .env.example                # Template for environment variables
```

## Running locally

1. Clone this repository and change into its directory.
2. Create a Python virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r scripts/requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your API keys and tokens.
4. Run the bot:

   ```bash
   python scripts/main.py
   ```

Generated videos and thumbnails will appear in the `out/` directory. If YouTube credentials are not provided the bot will skip uploading and leave the MP4 files in `out/`.

## GitHub Actions

The included workflow `.github/workflows/run.yml` runs automatically on a schedule at 06:07, 12:07 and 18:07 UTC every day. It can also be triggered manually via the Actions tab. The workflow installs dependencies, runs the bot and commits any new videos and thumbnails back to the repository.

### First run

On the first run, ensure that you have added all required secrets to the repository settings:

* `OPENAI_API_KEY` (required)
* `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD` (optional)
* `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (optional)
* `AFFILIATE_URL` (optional but recommended)

If YouTube tokens are missing, videos will still be generated and saved to the `out/` directory but will not be uploaded automatically.

## FAQ

**Where is the call‑to‑action / affiliate link set?**

The call‑to‑action is injected into the script, tweet and description using the `AFFILIATE_URL` secret. If this secret is not set a generic “Support the channel” link is used instead.

**How do I change the schedule?**

Edit the `cron` expression in `.github/workflows/run.yml`. The default schedule runs three times per day at 06:07, 12:07 and 18:07 UTC. Refer to [the GitHub Actions cron syntax](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule) for more options.

## License

This project is provided as‑is under the MIT license.
