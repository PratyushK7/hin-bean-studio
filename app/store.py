"""Small JSON files that several threads read and write (analytics, YouTube cache, topic state).

write() is atomic (temp file + replace), so a crash or a second writer can never leave half a file, and read() never
raises: a missing or damaged file just gives the default.
"""
import json, os, threading
from pathlib import Path

_locks, _guard = {}, threading.Lock()


def lock_for(path):
    with _guard:
        return _locks.setdefault(str(path), threading.RLock())


def read(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def write(path, obj, indent=1):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with lock_for(path):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(obj, indent=indent, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)
