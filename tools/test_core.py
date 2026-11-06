"""Small offline tests for the Hindi Explainer Studio core.

Run: python tools/test_core.py
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

import analytics
import store
import topics
import ytdata

def test_store() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "nested" / "state.json"
        store.write(path, {"हिंदी": "ठीक"})
        assert store.read(path) == {"हिंदी": "ठीक"}
        path.write_text("{broken", encoding="utf-8")
        assert store.read(path, {"fallback": True}) == {"fallback": True}

def test_topics() -> None:
    assert topics.classify("Why does the Moon look bigger?") == "Why"
    assert topics.classify("What if the Sun disappeared?") == "Scenario"
    assert topics.length_instructions(45).find("Hindi narration") >= 0
    assert "16:9" in topics.length_instructions(600)
    assert topics.VOICE_IDS == ["own_recording", "hindi_tts"]
    assert topics.LENGTHS["long"][0] == 480

def test_analytics() -> None:
    rows = [
        {"slot": "A", "type": "Why", "views": 100, "engaged_pct": 60, "avg_pct": 72, "subs": 2},
        {"slot": "A", "type": "Why", "views": 300, "engaged_pct": 50, "avg_pct": 64, "subs": 4},
    ]
    summary = analytics.summarize(rows)
    assert summary["by_slot"][0]["videos"] == 2
    assert summary["by_slot"][0]["avg_views"] == 200.0
    assert summary["by_type"][0]["type"] == "Why"
    current = [{"id": "x", "slot": "B", "notes": "Hindi label"}]
    fresh = [{"id": "x", "slot": None, "notes": None, "views": 1000}]
    merged = analytics.apply_edits(fresh, current)
    assert merged[0]["slot"] == "B" and merged[0]["notes"] == "Hindi label"

def test_youtube_duration() -> None:
    assert ytdata.seconds("PT1H2M3S") == 3723
    assert ytdata.seconds("PT44S") == 44
    assert ytdata.seconds("PT7M12S") == 432

if __name__ == "__main__":
    for fn in (test_store, test_topics, test_analytics, test_youtube_duration):
        fn()
        print("PASS", fn.__name__)
    print("All offline core tests passed.")
