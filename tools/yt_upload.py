"""yt_upload.py - upload a finished projects Short to YouTube, fill every field from its upload sheet, schedule it.

    .venv\\Scripts\\python yt_upload.py auth                                  sign in once (opens the browser)
    .venv\\Scripts\\python yt_upload.py upload <project> --slot A --date 2026-11-05 [--dry-run]
    .venv\\Scripts\\python yt_upload.py upload <project> --at "2026-11-05 12:00"   (IST)
    .venv\\Scripts\\python yt_upload.py upload <project> --now                    publish immediately, public
    .venv\\Scripts\\python yt_upload.py comment <project>                     post the pinned-comment text (after it's public)
    .venv\\Scripts\\python yt_upload.py status                                what's been uploaded

Reads projects\\<project>\\:
    <project>.mp4, <project>.srt, <project>-thumbnail.png, <project>-youtube.txt
and sets: title, description, tags, category Education, Hindi, not made for kids, altered content No,
private + publishAt (scheduled), custom thumbnail, Hindi captions from the .srt.
Writes <project>-upload.json with the video id, and refuses to upload the same project twice (--force overrides).

Uses the official YouTube Data API v3 with your own OAuth client (client_secret.json in tools\\.secrets\\).
Nothing is uploaded without the `upload` command; --dry-run shows exactly what would be sent.

Not possible through the API, so do these by hand in Studio: pin the comment and the Education fields
(Type: Concept overview, Level: None), plus anything marked "your call".
"""
import argparse, datetime as dt, json, os, re, sys, time
from pathlib import Path

# the projects folder: Bean Studio passes it in BEAN_PROJECTS_DIR; run by hand it is the projects folder next to tools/
ROOT = Path(os.environ.get("BEAN_PROJECTS_DIR") or Path(__file__).resolve().parent.parent / "projects")
SECRETS = Path(__file__).resolve().parent / ".secrets"
CLIENT = SECRETS / "client_secret.json"
TOKEN = SECRETS / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/yt-analytics.readonly"]   # the last two: Bean Studio reads your numbers
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
SLOTS = {"A": "19:00", "B": "12:00", "Long": "20:30"}   # IST, same as the local planner workbook
EDUCATION = "27"


# ---------- the upload sheet ----------
def read_sheet(proj):
    f = proj / f"{proj.name}-youtube.txt"
    if not f.exists(): sys.exit(f"missing {f} - write the upload sheet first (projects step 10)")
    sec, cur = {}, None
    for line in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^== (.+?) ==\s*$", line)
        if m: cur = m.group(1).upper(); sec[cur] = []; continue
        if cur: sec[cur].append(line)
    get = lambda k: "\n".join(sec.get(k, [])).strip()
    title = get("TITLE").split("\n\nAlternates:")[0].split("\nAlternates:")[0].strip()
    desc = get("DESCRIPTION")
    tags = [t.strip() for t in re.split(r",", get("TAGS").replace("\n", ",")) if t.strip()]
    settings = get("SETTINGS").lower()
    return {"title": title, "description": desc, "tags": tags, "comment": get("PINNED COMMENT"),
            "kids": "made for kids" in settings and "not made for kids" not in settings,
            "synthetic": bool(re.search(r"altered or synthetic content:\s*yes", settings))}

def check(meta):
    errs = []
    if not meta["title"]: errs.append("no title")
    if len(meta["title"]) > 100: errs.append(f"title is {len(meta['title'])} chars (max 100)")
    if len(meta["description"]) > 5000: errs.append("description over 5000 chars")
    if re.search(r"[<>]", meta["title"] + meta["description"]): errs.append("< or > in title/description (YouTube rejects them)")
    # YouTube counts tags with spaces as quoted; keep a margin under the 500-char limit
    while meta["tags"] and sum(len(t) + (2 if " " in t else 0) + 1 for t in meta["tags"]) > 480:
        meta["tags"].pop()
    return errs

def when(a):
    if a.at: t = dt.datetime.strptime(a.at, "%Y-%m-%d %H:%M")
    elif a.slot and a.date: t = dt.datetime.strptime(f"{a.date} {SLOTS[a.slot]}", "%Y-%m-%d %H:%M")
    else: sys.exit("give --at 'YYYY-MM-DD HH:MM' (IST) or --slot A|B|Long --date YYYY-MM-DD")
    t = t.replace(tzinfo=IST)
    if t < dt.datetime.now(IST) + dt.timedelta(minutes=30):
        sys.exit(f"{t:%d %b %H:%M} IST is in the past or under 30 min away - pick a later time")
    return t


# ---------- the API ----------
def service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    if not TOKEN.exists(): sys.exit("not signed in - run: yt_upload.py auth")
    creds = Credentials.from_authorized_user_file(str(TOKEN))   # the scopes it was granted, so an older token keeps working for uploads
    if not creds.valid:
        creds.refresh(Request()); TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def cmd_auth(a):
    from google_auth_oauthlib.flow import InstalledAppFlow
    if not CLIENT.exists():
        sys.exit(f"put your OAuth client file at {CLIENT} first (see SETUP in yt_upload.md)")
    creds = InstalledAppFlow.from_client_secrets_file(str(CLIENT), SCOPES).run_local_server(port=0)
    TOKEN.write_text(creds.to_json())
    ch = service().channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
    print(f"signed in as channel: {ch}")

def cmd_upload(a):
    proj = ROOT / a.project
    files = {k: proj / f"{a.project}{s}" for k, s in
             (("video", ".mp4"), ("srt", ".srt"), ("thumb", "-thumbnail.png"))}
    for k, f in files.items():
        if not f.exists(): sys.exit(f"missing {f}")
    log = proj / f"{a.project}-upload.json"
    if log.exists() and not a.force:
        sys.exit(f"already uploaded: {json.loads(log.read_text())['url']} (use --force to upload again)")
    meta = read_sheet(proj)
    errs = check(meta)
    if errs: sys.exit("fix the upload sheet: " + "; ".join(errs))
    t = dt.datetime.now(IST) if a.now else when(a)
    status = {"selfDeclaredMadeForKids": meta["kids"], "containsSyntheticMedia": meta["synthetic"],
              "embeddable": True, "license": "youtube"}
    if a.now: status["privacyStatus"] = "public"                      # publish immediately
    else: status.update(privacyStatus="private", publishAt=t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))   # private until then
    body = {
        "snippet": {"title": meta["title"], "description": meta["description"], "tags": meta["tags"],
                    "categoryId": EDUCATION, "defaultLanguage": "hi", "defaultAudioLanguage": "hi"},
        "status": status,
    }
    live = "NOW (public immediately)" if a.now else f"{t:%a %d %b %Y %H:%M} IST  ({t.astimezone(dt.timezone(dt.timedelta(hours=-5))):%a %H:%M} ET)"
    print(f"\n  {a.project}\n  goes live  {live}")
    print(f"  title      {meta['title']}")
    print(f"  desc       {meta['description'].splitlines()[0][:90]}  (+{len(meta['description'].splitlines()) - 1} lines)")
    print(f"  tags       {len(meta['tags'])}: {', '.join(meta['tags'])[:90]}...")
    print(f"  settings   Education, Hindi, made for kids: {meta['kids']}, altered content: {meta['synthetic']}")
    print(f"  files      {files['video'].name}, {files['thumb'].name}, {files['srt'].name}")
    if a.dry_run:
        print("\n  dry run - nothing sent"); return

    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    lock = proj / f"{a.project}-upload.lock"          # one upload of a video at a time: a double click or a second window is refused
    try:                                               # O_EXCL: creating the lock is atomic, so two processes can't both get it
        os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        if time.time() - lock.stat().st_mtime < 3 * 3600:
            sys.exit("another upload of this video is already running (delete " + lock.name + " if it crashed)")
        lock.write_text(str(os.getpid()))              # a lock left by a crash hours ago: take over
    try:
        yt = service()
        req = yt.videos().insert(part="snippet,status", body=body,
                                 media_body=MediaFileUpload(str(files["video"]), chunksize=8 * 1024 * 1024, resumable=True))
        resp, tries = None, 0
        while resp is None:
            try:
                st, resp = req.next_chunk()
                tries = 0
                if st: print(f"  uploading {int(st.progress() * 100)}%")
            except HttpError as e:                       # temporary server trouble: wait and resume where it stopped
                if e.resp.status in (500, 502, 503, 504) and tries < 5:
                    tries += 1; print(f"  YouTube said {e.resp.status}; retrying ({tries}/5)"); time.sleep(2 ** tries)
                else: raise
        return finish_upload(a, yt, files, resp, meta, t, log)
    finally:
        lock.unlink(missing_ok=True)

def finish_upload(a, yt, files, resp, meta, t, log):
    from googleapiclient.http import MediaFileUpload
    vid = resp["id"]
    print(f"  uploaded   https://youtu.be/{vid}")
    out = {"id": vid, "url": f"https://youtu.be/{vid}", "studio": f"https://studio.youtube.com/video/{vid}/edit",
           "publishAt": t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "now": bool(a.now), "title": meta["title"], "uploaded": dt.datetime.now(IST).isoformat()}
    log.write_text(json.dumps(out, indent=1))   # written before the extras, so a failure below can't cause a double upload
    try:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(files["thumb"]), mimetype="image/png")).execute()
        print("  thumbnail  set")
    except Exception as e:
        print(f"  thumbnail  FAILED ({e}). Custom thumbnails need a phone-verified channel; set it in Studio.")
    try:
        yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "hi", "name": "Hindi", "isDraft": False}},
                             media_body=MediaFileUpload(str(files["srt"]), mimetype="application/octet-stream")).execute()
        print("  captions   Hindi .srt added")
    except Exception as e:
        print(f"  captions   FAILED ({e}). Upload the .srt in Studio.")
    got = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]
    out["status"] = got; log.write_text(json.dumps(out, indent=1))
    if got.get("privacyStatus") == "private" and (a.now or not got.get("publishAt")):
        print("\n  WARNING: YouTube kept this video private" + (" although you asked to post it now." if a.now else " with no schedule.")
              + " If your API project hasn't passed the\n  YouTube API audit, uploads are locked private - see yt_upload.md.")
    print("\n  done. The API can't set these, so do them by hand in Studio (Details > Show more > Education):\n"
          "    Type: Concept overview | Level: None | Exam/course: None | Problems: empty\n"
          "    and pin the comment.\n  " + out["studio"])

def cmd_comment(a):
    proj = ROOT / a.project
    log = proj / f"{a.project}-upload.json"
    if not log.exists(): sys.exit("not uploaded yet")
    info = json.loads(log.read_text()); meta = read_sheet(proj)
    if not meta["comment"]: sys.exit("no PINNED COMMENT in the sheet")
    yt = service()
    r = yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": info["id"],
        "topLevelComment": {"snippet": {"textOriginal": meta["comment"]}}}}).execute()
    print(f"posted: {meta['comment']}\nnow pin it in Studio (the API can't pin): {info['studio'].replace('/edit', '/comments')}")

def cmd_status(a):
    for log in sorted(ROOT.glob("*/*-upload.json")):
        i = json.loads(log.read_text())
        print(f"{log.parent.name:18} {i['publishAt']}  {i['url']}  {i['title']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth").set_defaults(f=cmd_auth)
    p = sub.add_parser("upload"); p.add_argument("project"); p.add_argument("--at"); p.add_argument("--slot", choices=SLOTS)
    p.add_argument("--date"); p.add_argument("--now", action="store_true", help="publish immediately (public) instead of scheduling")
    p.add_argument("--dry-run", action="store_true"); p.add_argument("--force", action="store_true")
    p.set_defaults(f=cmd_upload)
    p = sub.add_parser("comment"); p.add_argument("project"); p.set_defaults(f=cmd_comment)
    sub.add_parser("status").set_defaults(f=cmd_status)
    a = ap.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
