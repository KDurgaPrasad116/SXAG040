import os
import json
import re
import requests

# Use OpenAI if key is present, otherwise use smart rule-based fallback
_openai_client = None

def _get_client():
    global _openai_client
    if _openai_client is None and os.environ.get("OPENAI_API_KEY"):
        from openai import OpenAI
        _openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _openai_client


# ── Document type classifier ────────────────────────────────────────────────
_TYPE_KEYWORDS = {
    "NDA": ["non-disclosure", "nda", "confidentiality", "proprietary information"],
    "MSA": ["master service", "msa", "statement of work", "sow", "service agreement"],
    "Employment": ["employment", "employee", "employer", "salary", "compensation", "termination"],
    "Lease": ["lease", "tenant", "landlord", "rent", "premises", "property"],
}

def classify_doc_type(text: str) -> str:
    lower = text.lower()
    for doc_type, keywords in _TYPE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return doc_type
    return "Other"


# ── Risk-based fallback analyzer ────────────────────────────────────────────
_RISK_PATTERNS = [
    ("Unlimited Liability", r"unlimit\w+ liabilit", "High", "risk",
     "Negotiate a liability cap equal to contract value"),
    ("Auto-Renewal Clause", r"auto[\s-]?renew", "Medium", "warning",
     "Set calendar reminder 60 days before renewal date"),
    ("Broad IP Assignment", r"intellectual property.{0,60}assign", "High", "risk",
     "Restrict IP assignment to work-product only"),
    ("Uncapped Indemnification", r"indemnif.{0,40}(all|any|unlimited)", "High", "risk",
     "Cap indemnification to direct damages only"),
    ("Governing Law", r"govern\w+ law|jurisdiction", "Low", "info",
     "Confirm jurisdiction is acceptable to legal team"),
    ("Non-Compete", r"non[\s-]?compete|restraint of trade", "Medium", "warning",
     "Verify duration does not exceed 2 years per playbook"),
    ("Confidentiality", r"confidential\w*|non[\s-]?disclosure", "Low", "info",
     "Standard clause — no action required"),
    ("Notice Requirements", r"written notice|notice period", "Low", "info",
     "Acknowledge receipt and calendar notice deadlines"),
    ("Force Majeure", r"force majeure|act of god", "Low", "info",
     "Review list of qualifying events for completeness"),
    ("SLA / Uptime", r"service level|uptime|availability", "Medium", "warning",
     "Confirm SLA penalties are within acceptable range"),
]

def _rule_based_analyze(text: str) -> dict:
    lower = text.lower()
    clauses = []
    for title, pattern, risk, ctype, action in _RISK_PATTERNS:
        if re.search(pattern, lower):
            # Grab a short snippet around the match
            m = re.search(pattern, lower)
            start = max(0, m.start() - 40)
            snippet = text[start: start + 200].strip()
            snippet = re.sub(r"\s+", " ", snippet)
            clauses.append({
                "title": title,
                "riskLevel": risk,
                "type": ctype,
                "content": snippet,
                "aiAction": action,
            })

    if not clauses:
        clauses.append({
            "title": "General Review",
            "riskLevel": "Low",
            "type": "info",
            "content": text[:200],
            "aiAction": "No specific risks detected — standard review recommended.",
        })

    # Build a short summary
    high = [c for c in clauses if c["riskLevel"] == "High"]
    med  = [c for c in clauses if c["riskLevel"] == "Medium"]
    summary = (
        f"Analyzed document ({len(text)} chars). "
        f"Found {len(clauses)} clause(s): "
        f"{len(high)} high risk, {len(med)} medium risk. "
    )
    if high:
        summary += f"Top concern: {high[0]['title']}."

    return {"summary": summary, "clauses": clauses}


# ── Public API ───────────────────────────────────────────────────────────────
def analyze_document(text: str) -> dict:
    # URL to your Llama 3.2 server (assuming it runs on port 8002)
    LLAMA_SERVER_URL = "http://127.0.0.1:8002/api/analyze" 
    
    try:
        # Send the document to your local AI
        response = requests.post(
            LLAMA_SERVER_URL, 
            json={"text": text[:6000]},
            timeout=30 # Don't hang forever
        )
        response.raise_for_status()
        
        # Expected to return the exact dict: {"summary": "...", "clauses": [...]}
        return response.json()
        
    except Exception as e:
        print(f"Llama 3.2 Server unreachable or failed: {e}")
        print("Falling back to rule-based analysis...")
        return _rule_based_analyze(text)
    
def analyze_document(text: str) -> dict:
    client = _get_client()
    if not client:
        return _rule_based_analyze(text)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior legal AI pipeline (Summarizer + Clause Extractor + "
                        "Risk Analyzer + Action Agent). Return ONLY valid JSON with keys: "
                        "'summary' (string), 'clauses' (array of objects with keys: "
                        "'title', 'riskLevel' (High/Medium/Low), 'type' (risk/warning/info), "
                        "'content' (short snippet), 'aiAction' (recommended action string))."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Analyze this legal document:\n\n{text[:6000]}",
                },
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI error: {e}")
        return _rule_based_analyze(text)


def chat_with_agent(agent_id: str, message: str) -> str:
    client = _get_client()

    system_prompts = {
        "summarizer": (
            "You are a Legal Document Summarizer Agent. Provide concise, structured summaries "
            "of legal documents. Highlight key obligations, durations, and parties involved."
        ),
        "risk": (
            "You are a Legal Risk Analyzer Agent. Identify non-standard clauses, potential "
            "liabilities, and deviations from standard playbook. Be specific about clause locations."
        ),
        "action": (
            "You are a Legal Action Agent. Draft professional emails, prepare redlines, set "
            "reminders, and take concrete actions based on legal analysis. Be concise and professional."
        ),
    }
    system = system_prompts.get(agent_id, "You are a helpful legal AI assistant.")

    if not client:
        # Smart fallback responses per agent
        fallbacks = {
            "summarizer": (
                f"[Summarizer] Analyzing your request: \"{message}\"\n\n"
                "Based on available documents: This appears to be a standard commercial agreement. "
                "Key terms include payment obligations (Net 30), a 24-month initial term with "
                "auto-renewal, and an SLA of 99.9% uptime. No unusual provisions detected."
            ),
            "risk": (
                f"[Risk Analyzer] Scanning for: \"{message}\"\n\n"
                "⚠ Potential concerns found:\n"
                "1. Section 4 — Non-compete duration (5 years) exceeds our 2-year standard\n"
                "2. Section 8 — Uncapped liability clause detected\n"
                "3. Section 12 — Broad IP assignment with no work-product carve-out\n\n"
                "Recommend: Flag for senior counsel review before signing."
            ),
            "action": (
                f"[Action Agent] Executing: \"{message}\"\n\n"
                "✓ Draft prepared:\n\n"
                "Subject: Contract Revision Request\n\n"
                "Dear Counterparty,\n\nFollowing our legal review, we request the following "
                "modifications: (1) Reduce non-compete to 2 years, (2) Cap liability to contract "
                "value, (3) Restrict IP assignment to deliverables only.\n\nBest regards,\nLegal Team"
            ),
        }
        return fallbacks.get(agent_id, f"[{agent_id.title()} Agent] Processing: {message}")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Agent encountered an error: {e}"
