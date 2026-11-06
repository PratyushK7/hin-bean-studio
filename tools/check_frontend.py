"""Extract the local dashboard's inline JavaScript and ask Node to syntax-check it."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "app" / "static" / "index.html"

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.external = False
        self.current: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            self.inside = True
            self.external = any(k.lower() == "src" for k, _ in attrs)
            self.current = []

    def handle_data(self, data):
        if self.inside and not self.external:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.inside:
            if self.current:
                self.blocks.append("".join(self.current))
            self.inside = False
            self.external = False
            self.current = []

def main() -> int:
    parser = Scripts()
    parser.feed(HTML.read_text(encoding="utf-8"))
    if not parser.blocks:
        raise SystemExit("No inline JavaScript found in app/static/index.html")
    source = "\n\n".join(parser.blocks)
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as f:
        f.write(source)
        path = Path(f.name)
    try:
        result = subprocess.run(["node", "--check", str(path)], check=False)
        if result.returncode:
            return result.returncode
    finally:
        path.unlink(missing_ok=True)
    print("Frontend JavaScript syntax OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
