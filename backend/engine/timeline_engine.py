def build_timeline(logs, git_data):
    items = []
    for c in git_data.get("commits", []):
        items.append({"timestamp": c["timestamp"], "type": "git",
                      "description": f'Commit {c["hash"]}: {c["message"]}'})
    for e in logs.get("events", []):
        if e["level"] in {"ERROR", "WARN"}:
            items.append({"timestamp": e["timestamp"], "type": "log",
                          "description": e["message"]})
    return sorted(items, key=lambda x: x["timestamp"])
