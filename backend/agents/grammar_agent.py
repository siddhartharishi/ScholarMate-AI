import json, os, random
from dotenv import load_dotenv
from agents.config.llm import generate
from agents.config.states import ReportState
from chunker.token_chunker import combine_text
from langsmith import traceable
load_dotenv()

@traceable(name="grammar_agent")
def grammar_check_agent(state: ReportState) -> ReportState:
    text = combine_text(state)

    # optional sampling (recommended)
    text = text[:5000]

    prompt = f"""
You are a balanced academic writing reviewer.

Evaluate ONLY grammar and writing quality.

HIGH:
- Clear, well-structured
- Minimal errors

MEDIUM:
- Mostly clear, some issues

LOW:
- Poor grammar, hard to read

IMPORTANT:
Most research papers are HIGH or MEDIUM.
Only give LOW if clearly poor.

Text:
{text}

Return ONLY JSON:
{{
  "grammar_rating": "high" | "medium" | "low"
}}
"""

    response = generate(prompt)

    try:
        result = json.loads(response)
        rating = result.get("grammar_rating", "medium").lower()

        if rating not in ["high", "medium", "low"]:
            rating = "medium"

        state["grammar_rating"] = rating

    except:
        state["grammar_rating"] = "medium"

    return state