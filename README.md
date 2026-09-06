# RootCause AI

A hackathon MVP for investigating production incidents by correlating application logs,
stack traces, Git history/diffs, and source-code context. Featherless.ai is the reasoning layer.

## Run backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload

## Run frontend
cd frontend
npm install
npm run dev

Backend: http://localhost:8000
Frontend: http://localhost:5173

Set FEATHERLESS_API_KEY in backend/.env for real Featherless reasoning.
Without a key, the deterministic fallback keeps the demo runnable locally.

## Demo files
test_data/demo_repo.zip
test_data/application.log
test_data/stacktrace.txt
