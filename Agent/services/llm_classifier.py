import json
import requests
import re


# 🔹 Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:latest"   # change if needed: llama3:8b / llama3:instruct


def classify_clause(clause: str):
    """
    Classify a legal clause using local LLaMA model (Ollama)
    """

    prompt = f"""
You are a legal AI assistant.

Analyze the clause and return JSON.

Clause: "{clause}"

Return strictly in this JSON format:
{{
  "type": "Positive | Negative | Neutral",
  "explanation": "short explanation",
  "risk": "Low | Medium | High",
  "action": "Accept | Review | Reject",
  "benefit_score": number (1-10)
}}

Rules:
- Only return JSON
- No extra text
- benefit_score must be between 1 and 10
"""

    try:
        # 🔹 Call Ollama API
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        output = result.get("response", "").strip()

        # 🔥 Extract JSON safely (handles messy LLaMA output)
        json_match = re.search(r"\{.*\}", output, re.DOTALL)

        if not json_match:
            raise ValueError("No valid JSON found in response")

        parsed = json.loads(json_match.group())

        # 🔹 Normalize values (extra safety)
        parsed["type"] = parsed.get("type", "Neutral")
        parsed["explanation"] = parsed.get("explanation", "")
        parsed["risk"] = parsed.get("risk", "Unknown")
        parsed["action"] = parsed.get("action", "Review")

        # Ensure valid score
        score = parsed.get("benefit_score", 5)
        if not isinstance(score, int):
            score = 5
        score = max(1, min(score, 10))
        parsed["benefit_score"] = score

        # 🔹 Add original clause
        parsed["clause"] = clause

        return parsed

    except Exception as e:
        # 🔥 Fallback (never crash system)
        return {
            "clause": clause,
            "type": "Neutral",
            "explanation": f"Processing error: {str(e)}",
            "risk": "Unknown",
            "action": "Review",
            "benefit_score": 5
        }