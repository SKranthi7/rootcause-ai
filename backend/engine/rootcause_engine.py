import json, os
from openai import OpenAI

SYSTEM_PROMPT = """You are RootCause AI, a production incident investigator.
Analyze only supplied evidence. Do not invent facts. Distinguish symptoms from root cause.
Return ONLY JSON with: root_cause, confidence, severity, suspected_commit,
reasoning, recommended_actions. confidence is 0..1.
"""

def fallback(e):
    changes = e.get("recent_changes", [])
    commit = changes[0]["commit"] if changes else None
    if e.get("exception") == "NullPointerException":
        root = "A null value is being dereferenced at the failing source line."
        if changes:
            root = "A recent change to the failing file is the strongest suspected cause of the null dereference."
        severity = "CRITICAL"
    else:
        root = "The failing stack-trace location is the strongest available root-cause candidate."
        severity = "HIGH"
    return {
        "root_cause": root, "confidence": e.get("confidence", .5),
        "severity": severity, "suspected_commit": commit,
        "reasoning": e.get("signals", []),
        "recommended_actions": [
            "Inspect the highlighted source line and recent commit.",
            "Add a regression test covering the failing input.",
            "Rollback the latest deployment if the incident is still active."
        ]
    }

def analyze_with_featherless(evidence):
    key = os.getenv("FEATHERLESS_API_KEY")
    if not key:
        return fallback(evidence)
    client = OpenAI(api_key=key,
        base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"))
    response = client.chat.completions.create(
        model=os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        temperature=0.1,
        messages=[
            {"role":"system", "content":SYSTEM_PROMPT},
            {"role":"user", "content":json.dumps(evidence, indent=2)}
        ]
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return fallback(evidence)
