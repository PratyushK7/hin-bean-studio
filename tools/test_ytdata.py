"""Tests app/ytdata.py against a fake YouTube (no network, no sign-in). Run: .venv\\Scripts\\python tools\\test_ytdata.py"""
import datetime as dt, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
import ytdata

PUBLISHED = {   # id -> (title, publishedAt UTC, duration)
    "v1": ("Why Does Caffeine Stay in Your Body?", "2026-11-03T13:30:00Z", "PT44S"),    # 12:00 IST  -> slot A
    "v2": ("How GPS Finds Your Exact Location", "2026-11-04T06:30:00Z", "PT44S"),   # 06:30 IST -> slot B
    "v3": ("A scheduled one", "2026-11-09T01:00:00Z", "PT40S"),
    "v4": ("How Satellites Map the Earth", "2026-11-08T15:00:00Z", "PT7M12S"),   # long
}


class Req:
    def __init__(self, fn): self.fn = fn
    def execute(self): return self.fn()


class Fake:
    calls = {}
    def __init__(self, kind): self.kind = kind
    def channels(self): return self
    def playlistItems(self): return self
    def videos(self): return self
    def reports(self): return self
    def list(self, **kw):
        if "mine" in kw:
            return Req(lambda: {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU1"}}, "statistics": {"subscriberCount": "42"}, "snippet": {"title": "Hindi Explainer Studio"}}]})
        if "playlistId" in kw:
            return Req(lambda: {"items": [{"contentDetails": {"videoId": i}} for i in PUBLISHED]})
        ids = kw["id"].split(",")
        return Req(lambda: {"items": [{"id": i, "snippet": {"title": PUBLISHED[i][0], "publishedAt": PUBLISHED[i][1]},
                                       "contentDetails": {"duration": PUBLISHED[i][2]},
                                       "status": {"privacyStatus": "private" if i == "v3" else "public"}} for i in ids]})
    def query(self, **kw):
        Fake.calls[kw.get("dimensions")] = Fake.calls.get(kw.get("dimensions"), 0) + 1
        def run():
            if kw.get("dimensions") == "video":
                return {"columnHeaders": [{"name": n} for n in ["video"] + kw["metrics"].split(",")],
                        "rows": [["v1", 1200, 840, 2000, 31, 70.5, 40, 5, 9, 3], ["v2", 3400, 2900, 5200, 33, 75.0, 120, 20, 40, 9],
                                 ["v4", 900, 900, 3000, 200, 30.0, 10, 1, 2, 1]]}
            if kw.get("dimensions") == "elapsedVideoTimeRatio":   # a curve with a cliff at 20%
                return {"rows": [[i / 100, 0.9 - (0.4 if i >= 20 else 0) - i * 0.002] for i in range(1, 101)]}
            return {"rows": [["IN", 700], ["US", 300]]}
        return Req(run)


def main():
    import googleapiclient.discovery as d
    d.build = lambda name, ver, **kw: Fake(name)
    ytdata.credentials = lambda ROOT: object()
    cfg = {"projects_dir": str(ROOT / "projects"), "planner": str(ROOT / "data/planner.xlsx"), "slots": {"A": "19:00", "B": "12:00", "Long": "20:30"}}
    existing = [{"title": "Why Does Caffeine Stay in Your Body?", "type": "Why", "notes": "mine", "slot": None}]
    rows, info = ytdata.sync(ROOT, cfg, existing)
    by = {r["id"]: r for r in rows}
    assert info["videos"] == 3 and "v3" not in by, "private/scheduled videos must be skipped"
    assert by["v1"]["slot"] == "A" and by["v2"]["slot"] == "B" and by["v4"]["slot"] == "Long", (by["v1"]["slot"], by["v2"]["slot"], by["v4"]["slot"])
    assert by["v1"]["notes"] == "mine" and by["v1"]["type"] == "Why", "hand-set fields survive"
    assert by["v1"]["views"] == 1200 and by["v1"]["engaged_pct"] == 70.0, by["v1"]["engaged_pct"]
    assert by["v1"]["avg_pct"] == 70.5 and by["v1"]["subs"] == 3
    assert abs(by["v1"]["drop_s"] - 0.2 * 44) < 1.5, by["v1"]["drop_s"]
    assert by["v1"]["geo"] == "IN 58%, US 25%", by["v1"]["geo"]
    assert by["v2"]["type"] in ("How many", None)
    assert by["v1"]["retention"][0][0] <= 5 and len(by["v1"]["retention"]) >= 8
    print("sync ok:", {k: by["v1"][k] for k in ("slot", "type", "views", "engaged_pct", "drop_s", "geo", "posted")})
    # a second sync with the first result keeps manual edits and doesn't duplicate rows
    by["v2"]["type"] = "Timeline"
    rows2, _ = ytdata.sync(ROOT, cfg, list(by.values()))
    assert len(rows2) == 3 and {r["id"]: r for r in rows2}["v2"]["type"] == "Timeline"
    # incremental details: an old video that was checked today is not queried again; a new one still is
    old = {r["id"]: r for r in rows2}
    ytdata.FRESH_DAYS = -1                                   # the fake videos are days old; treat them as "old" here
    old["v1"]["detail_checked"] = dt.date.today().isoformat()
    for k in ("v2", "v4"): old[k]["detail_checked"] = None
    Fake.calls.clear(); ytdata.sync(ROOT, cfg, list(old.values()))
    assert Fake.calls.get("elapsedVideoTimeRatio") == 2, Fake.calls      # v2 and v4 refreshed, v1 skipped
    print("incremental details ok:", Fake.calls)
    print("resync ok, rows:", len(rows2))
    assert ytdata.seconds("PT1H2M3S") == 3723 and ytdata.seconds("PT44S") == 44 and ytdata.seconds("PT7M12S") == 432
    print("all passed")


if __name__ == "__main__":
    main()
