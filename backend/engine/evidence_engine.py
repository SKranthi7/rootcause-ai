def build_evidence(logs, trace, git_data, code_context, timeline):
    target, line = trace.get("file"), trace.get("line")
    matching = []
    for c in git_data.get("commits", []):
        for ch in c.get("changed_files", []):
            if target and ch.get("file", "").endswith(target):
                matching.append({"commit": c["hash"], "message": c["message"],
                                  "file": ch["file"], "diff": ch["diff"]})
    score, signals = 0, []
    if trace.get("exception") != "UnknownException":
        score += 20; signals.append("A concrete exception was extracted from the stack trace.")
    if target and line:
        score += 20; signals.append(f"The stack trace points to {target}:{line}.")
    if matching:
        score += 25; signals.append("The failing file was modified in recent Git history.")
    if any("null" in x["diff"].lower() for x in matching):
        score += 15; signals.append("A recent diff contains null-related logic.")
    if logs.get("error_count", 0):
        score += 10; signals.append(f'{logs["error_count"]} error/exception events were detected.')
    return {
        "service": "payment-service",
        "exception": trace.get("exception"),
        "file": target, "line": line,
        "code_context": code_context,
        "recent_changes": matching,
        "timeline": timeline,
        "signals": signals,
        "confidence": min(score, 100) / 100
    }
