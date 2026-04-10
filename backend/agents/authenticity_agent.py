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
    You are a strict research integrity reviewer.

    Your task is to estimate the probability that a research paper contains fabricated, exaggerated, or unreliable claims.

    ---

    Paper Content:
    {text}

    ---

    Evaluate based on:

    1. Statistical anomalies:
    - suspiciously perfect results (e.g., repeated 100%, 0.00 loss)
    - overly rounded or identical numbers
    - unrealistic improvements

    2. Logical consistency:
    - claims in conclusions not supported by results
    - missing explanation of how results were obtained
    - gaps between methodology and outcomes

    3. Scientific rigor:
    - lack of experimental detail
    - vague descriptions of datasets or evaluation
    - absence of baseline comparisons

    4. Writing patterns:
    - generic or vague phrasing
    - repeated buzzwords without substance
    - LLM-like verbosity without specifics


    Do NOT use markdown.
    Do NOT wrap in ```json```.
    Return ONLY JSON:
    {{
        "authenticity_score": 0-100
    }}
    """
        
    response = generate(prompt)
    try:
        result = json.loads(response)
        state["authenticity_score"] = int(result["authenticity_score"])

    except Exception:
        state["authenticity_score"] = 0

    return state