import re
from pathlib import Path

JAVA = re.compile(r"at\s+[\w.$<>]+\(([^:()]+):(\d+)\)")
PY = re.compile(r'File "([^"]+)", line (\d+), in ([\w<>]+)')

def parse_stacktrace(path: Path):
    text = path.read_text(errors="ignore")
    exception = "UnknownException"
    for line in text.splitlines():
        s = line.strip()
        if ("Exception" in s or "Error" in s or "Throwable" in s) and not s.startswith("at "):
            exception = s.split(":")[0]
            break
    frames = []
    for line in text.splitlines():
        m = JAVA.search(line)
        if m:
            frames.append({"file": m.group(1), "line": int(m.group(2))})
        m = PY.search(line)
        if m:
            frames.append({"file": m.group(1), "line": int(m.group(2)), "method": m.group(3)})
    first = frames[0] if frames else {}
    return {"exception": exception, "frames": frames,
            "file": first.get("file"), "line": first.get("line")}
