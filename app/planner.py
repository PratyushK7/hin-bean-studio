"""bean-planner.xlsx, read once per change and shared by every tab (the schedule, topic de-duplication, video types).

rows(path) -> (list of dicts, error or None). The parse is cached until the file's modified time changes, and a file
that is missing or locked by Excel gives ([], "reason") instead of breaking the caller.
"""
import datetime as dt, threading
from pathlib import Path

_cache = {"key": None, "rows": []}
_lock = threading.Lock()
COLS = {"Post date (IST)": "date", "Slot": "slot", "Post time (IST)": "time", "Format": "format", "Video type": "type",
        "Working title": "title", "Status": "status", "Notes": "notes"}


def rows(path):
    p = Path(path)
    try:
        key = (str(p), p.stat().st_mtime)
    except OSError:
        return [], f"no planner file at {p}"
    with _lock:
        if _cache["key"] == key:
            return _cache["rows"], None
        try:
            import openpyxl
            ws = openpyxl.load_workbook(p, read_only=True, data_only=True)["Schedule"]
            head = [c.value for c in next(ws.iter_rows(min_row=3, max_row=3))]
            idx = {COLS[h]: i for i, h in enumerate(head) if h in COLS}
            out = []
            for r in ws.iter_rows(min_row=4, values_only=True):
                d = r[idx["date"]] if "date" in idx else None
                if isinstance(d, dt.datetime): d = d.date()
                if not isinstance(d, dt.date): continue
                row = {k: r[i] for k, i in idx.items()}
                row["date"] = d
                out.append(row)
            _cache.update(key=key, rows=out)
            return out, None
        except PermissionError:
            return _cache["rows"], "the planner is locked (open in Excel?); showing the last copy"
        except Exception as e:
            return _cache["rows"], f"could not read the planner: {str(e)[:120]}"


def titles(path):
    """every working title in the planner"""
    return [str(r["title"]) for r in rows(path)[0] if r.get("title")]


def types_by_title(path):
    return {str(r["title"]).strip().lower(): r["type"] for r in rows(path)[0] if r.get("title") and r.get("type")}
