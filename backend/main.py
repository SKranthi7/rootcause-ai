import shutil, tempfile
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from analyzers.log_analyzer import parse_log
from analyzers.stacktrace_analyzer import parse_stacktrace
from analyzers.git_analyzer import analyze_git_repo
from analyzers.code_analyzer import get_code_context
from engine.evidence_engine import build_evidence
from engine.timeline_engine import build_timeline
from engine.rootcause_engine import analyze_with_featherless

load_dotenv()
app = FastAPI(title="RootCause AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"name": "RootCause AI", "status": "running"}

@app.post("/api/analyze")
async def analyze_incident(repository: UploadFile = File(...),
                           log_file: UploadFile = File(...),
                           stacktrace_file: UploadFile = File(...)):
    if not repository.filename.endswith(".zip"):
        raise HTTPException(400, "Repository must be a .zip file.")

    workdir = Path(tempfile.mkdtemp(prefix="rootcause_"))
    try:
        repo_zip = workdir / "repo.zip"
        log_path = workdir / "application.log"
        trace_path = workdir / "stacktrace.txt"
        repo_zip.write_bytes(await repository.read())
        log_path.write_bytes(await log_file.read())
        trace_path.write_bytes(await stacktrace_file.read())

        repo_dir = workdir / "repo"
        shutil.unpack_archive(repo_zip, repo_dir, "zip")
        children = [p for p in repo_dir.iterdir() if p.is_dir()]
        actual_repo = children[0] if len(children) == 1 and (children[0]/".git").exists() else repo_dir

        logs = parse_log(log_path)
        trace = parse_stacktrace(trace_path)
        git_data = analyze_git_repo(actual_repo)
        code_context = get_code_context(actual_repo, trace)
        timeline = build_timeline(logs, git_data)
        evidence = build_evidence(logs, trace, git_data, code_context, timeline)
        result = analyze_with_featherless(evidence)

        return {
            "incident": {
                "service": evidence["service"],
                "severity": result.get("severity", "UNKNOWN"),
                "root_cause": result.get("root_cause", "Unknown"),
                "confidence": result.get("confidence", evidence["confidence"]),
                "affected_file": trace.get("file"),
                "affected_line": trace.get("line"),
                "suspected_commit": result.get("suspected_commit")
            },
            "reasoning": result.get("reasoning", []),
            "recommended_actions": result.get("recommended_actions", []),
            "evidence": evidence,
            "timeline": timeline
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
