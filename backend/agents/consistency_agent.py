import json, os
from dotenv import load_dotenv
from agents.config.llm import generate
from agents.config.states import ReportState
from langsmith import traceable
load_dotenv()

def get_section_headings(state: ReportState):
    return [sec.get("heading", "") for sec in state.get("sections", [])]

def classify_sections(headings: list[str]) -> dict:
    prompt = f"""
You are an expert in analyzing research paper structure.

Classify each section heading into ONE of:
- "methodology" → describes method, model, approach, architecture
- "results" → experiments, evaluation, findings, analysis
- "other" → everything else

---

Headings:
{headings}

---

Return ONLY JSON in this exact format:

{{
  "classification": [
    {{ "heading": "...", "type": "methodology | results | other" }}
  ]
}}
"""

    response = generate(prompt)

    try:
        result = json.loads(response)
        return result.get("classification", [])
    except:
        return []
    
def trim_text(text, max_len=6000):
    return text[:max_len]

def extract_sections_from_classification(state: ReportState, classification):
    method_text = []
    results_text = []

    for sec in state.get("sections", []):
        heading = sec.get("heading", "")
        body = sec.get("body", "")

        match = next(
            (c for c in classification if c["heading"] == heading),
            None
        )

        if not match:
            continue

        if match["type"] == "methodology":
            method_text.append(body)

        elif match["type"] == "results":
            results_text.append(body)

    return "\n\n".join(method_text), "\n\n".join(results_text)


@traceable(name="consistency_agent")
def consistency_agent(state: ReportState) -> ReportState:
    headings = get_section_headings(state)

    classification = classify_sections(headings)

    method_text, results_text = extract_sections_from_classification(
        state, classification
    )

    # fallback (only if completely empty)
    if not method_text:
        method_text = state.get("abstract", "")
    if not results_text:
        results_text = state.get("abstract", "")

    method_text = method_text[:6000]
    results_text = results_text[:6000]

    # print("method txt: ", method_text)
    # print("results_text: ", results_text)

    prompt = f"""
        You are a strict academic reviewer.
        Your task is to determine whether the RESULTS of a research paper are logically supported by its METHODOLOGY.

        Methodology:
        {method_text}

        Results:
        {results_text}

        Evaluate:
        - Are the experiments aligned with the described method?
        - Are the claims supported by the described setup?
        - Are there missing steps or unexplained jumps?
        - Are results exaggerated beyond methodology?

        Score:
        - 80 - 100 - strong alignment, well-supported
        - 50 - 79 - partially supported, some gaps
        - 0 - 49 - weak or unsupported claims

        Do NOT use markdown.
        Do NOT wrap in ```json```.
        Return ONLY JSON:
        {{
            "consistency_score": 0-100,
        }}
    """


    response = generate(prompt)
    # print("response in cnsitentcy: ", response)
    try:
        result = json.loads(response)

        score = int(result.get("consistency_score", 50))
        score = max(0, min(100, score))

        state["consistency_score"] = score

    except:
        state["consistency_score"] = 50

    return state


   