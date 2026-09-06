from pathlib import Path
from git import Repo, InvalidGitRepositoryError

def analyze_git_repo(repo_path: Path):
    try:
        repo = Repo(repo_path)
        commits = []
        for c in list(repo.iter_commits(max_count=10)):
            changes = []
            if c.parents:
                for d in c.parents[0].diff(c):
                    changes.append({
                        "file": d.b_path or d.a_path,
                        "change_type": d.change_type,
                        "diff": (d.diff or b"").decode("utf-8", errors="ignore")[:5000]
                    })
            commits.append({
                "hash": c.hexsha[:8],
                "message": c.message.strip(),
                "timestamp": c.committed_datetime.isoformat(),
                "changed_files": changes
            })
        return {"available": True, "commits": commits}
    except (InvalidGitRepositoryError, ValueError):
        return {"available": False, "commits": []}
