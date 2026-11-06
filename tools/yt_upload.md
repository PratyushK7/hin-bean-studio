# YouTube uploader setup

The uploader uses the official YouTube Data API with your own Google Cloud project. OAuth files remain local under `tools/.secrets/` and are excluded from Git.

## One-time setup

1. Create a Google Cloud project and enable **YouTube Data API v3** and **YouTube Analytics API**.
2. Configure the OAuth consent screen and add your Google account as a test user if the app is in Testing.
3. Create an OAuth client ID with application type **Desktop app**.
4. Save the downloaded client JSON as `tools/.secrets/client_secret.json`.
5. Run `python tools/yt_upload.py auth` from the repository root and sign in with the account that owns the channel.

The uploader stores its token at `tools/.secrets/token.json`. Do not commit either file.

## Video project files

Each project directory under `projects/<slug>/` should contain:

- `<slug>.mp4`
- `<slug>.srt` — Hindi captions/subtitles
- `<slug>-thumbnail.png`
- `<slug>-youtube.txt` — title, description, tags and upload settings

## Upload and schedule

Dry-run first:

```bash
python tools/yt_upload.py upload <slug> --at "2026-11-10 19:00" --dry-run
```

Schedule after reviewing the metadata:

```bash
python tools/yt_upload.py upload <slug> --at "2026-11-10 19:00"
```

Publish immediately only when explicitly intended:

```bash
python tools/yt_upload.py upload <slug> --now
```

The default slots are IST: A 19:00, B 12:00, Long 20:30. Change them in Settings and keep the planner consistent.

## Known YouTube API limitations

- An unaudited API project may be restricted to Private uploads. Complete YouTube's API audit if required before relying on public scheduling.
- The API cannot set every Education metadata field or pin comments. The uploader reports what must be completed manually in YouTube Studio.
- Analytics data is delayed and some Studio metrics are not available through the API.
