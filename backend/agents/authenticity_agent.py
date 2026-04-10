import json, os
from dotenv import load_dotenv
from typing import TypedDict, List
from agents.config.llm import generate
from agents.config.states import ReportState
from chunker.token_chunker import combine_text

load_dotenv()

from langsmith import traceable
@traceable(name="authenticity_agent")
def authenticity_agent(state: ReportState) -> ReportState:
    text = combine_text(state)

    prompt = f"""
    You are a balanced research integrity evaluator.

    Your task is to estimate the probability that a research paper contains fabricated, exaggerated, or unreliable claims.

    ---

    Scoring Guidelines:

    81–100:
    - Highly trustworthy
    - Strong methodology, realistic results, well-supported claims

    61–80:
    - Mostly reliable
    - Minor concerns but generally sound

    41-60:
    - Some concerns
    - Possible gaps in explanation or weak validation

    21-40:
    - Likely unreliable
    - Significant inconsistencies or missing rigor

    0-20:
    - Highly suspicious
    - Strong signs of fabrication or unsupported claims

    ---

    IMPORTANT:
    - Do NOT assign high scores unless there are clear red flags
    - Minor imperfections should NOT significantly increase the score

    ---

    Evaluate based on:

    1. Statistical anomalies (only if clearly unrealistic)
    2. Logical consistency between method and results
    3. Scientific rigor (datasets, baselines, reproducibility)
    4. Writing patterns (only if strongly indicative of fabrication)

    ---

    Paper Content:
    {text[:6000]}

    ---

    Return ONLY JSON:
    {{
        "authenticity_score": number (0-100)
    }}
"""    
    response = generate(prompt)
    try:
        result = json.loads(response)
        state["authenticity_score"] = int(result["authenticity_score"])

    except Exception:
        state["authenticity_score"] = 0

    return state