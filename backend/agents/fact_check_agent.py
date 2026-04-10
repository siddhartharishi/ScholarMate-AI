import json, os
from dotenv import load_dotenv
from agents.config.llm import generate
from agents.config.states import ReportState
from chunker.token_chunker import combine_text
from langsmith import traceable

load_dotenv()

@traceable(name="fact_check_agent")
def fact_check_agent(state: ReportState) -> ReportState:
    text = combine_text(state)

    prompt = f"""
        You are a fact-checking agent for research papers.
        Your task is to verify ONLY objective, factual claims.

        Rules:

        1. ONLY verify claims that are:
        - numerical values (constants, accuracy, percentages, metrics)
        - scientific formulas or laws
        - historical or well-established facts
        - dataset or benchmark references

        2. IGNORE:
        - opinions or interpretations
        - vague or subjective claims
        - statements that cannot be verified externally

        3. If the claim is NOT a verifiable fact, return false.

        4. If evidence clearly supports the claim → true

        5. If evidence contradicts or is missing → false

        Do NOT use markdown.
        Do NOT wrap in ```json```.
        Return ONLY JSON:
        {{
        "claims": [
            {{
            "claim": "text",
            "verified": true/false
            }}
        ]
        }}

        Be strict and only include meaningful factual claims.

        TEXT:
        {text}
    """

    response = generate(prompt)
    # print("facts: ", response['claims'])
    try:
        result = json.loads(response)

        claims = result.get("claims", [])

        # normalize into FactCheckState list
        state["fact_check"] = [
            {
                "claim": c["claim"],
                "verified": c["verified"]
            }
            for c in claims
        ]

    except Exception:
        state["fact_check"] = []

    return state