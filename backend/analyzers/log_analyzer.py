import re
from pathlib import Path

LINE_RE = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}).*?"
    r"(?P<level>ERROR|WARN|WARNING|INFO|DEBUG).*?(?P<message>.*)$", re.I)

def parse_log(path: Path):
    events = []
    for raw in path.read_text(errors="ignore").splitlines():
        m = LINE_RE.search(raw)
        if m:
            events.append({
                "timestamp": m.group("timestamp"),
                "level": m.group("level").upper(),
                "message": m.group("message").strip()
            })
    errors = [e for e in events if e["level"] == "ERROR" or "exception" in e["message"].lower()]
    return {"events": events, "errors": errors, "error_count": len(errors)}
