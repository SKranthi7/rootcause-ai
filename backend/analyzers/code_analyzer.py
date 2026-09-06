from pathlib import Path

def get_code_context(repo_path: Path, trace: dict):
    target, line = trace.get("file"), trace.get("line")
    if not target or not line:
        return {"file": target, "line": line, "code": ""}
    matches = list(repo_path.rglob(Path(target).name))
    if not matches:
        return {"file": target, "line": line, "code": ""}
    path = matches[0]
    lines = path.read_text(errors="ignore").splitlines()
    start, end = max(0, line-6), min(len(lines), line+5)
    code = "\n".join(f"{i+1:4}: {lines[i]}" for i in range(start, end))
    return {"file": str(path.relative_to(repo_path)), "line": line, "code": code}
