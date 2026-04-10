import json, os
from dotenv import load_dotenv
load_dotenv()
from typing import TypedDict, List
# from google import genai
from agents.config.states import ReportState, FactCheckState
from agents.config.llm import generate
from report.renderer import render_docx, convert_to_pdf


  
def synthesizer_agent(state: ReportState) -> ReportState:

    # Build compact context
    context = f"""
    TITLE: {state.get("title")}

    ABSTRACT: {state.get("abstract")}

    GRAMMAR: {state.get("grammar_rating")}
    CONSISTENCY SCORE: {state.get("consistency_score")}
    AUTHENTICITY SCORE: {state.get("authenticity_score")}

    NOVELTY:
    {state.get("novelty")}

    FACT CHECK:
    {state.get("fact_check")}
    """

    prompt = f"""
        You are a research review expert.

        Based on the following evaluation:

        1. Summarize the paper in 5-6 lines (executive summary)
        2. Evaluate overall quality
        3. Decide recommendation:
        - PASS (worthy for research)
        - FAIL (not strong enough)

        Be critical and balanced.
        Do NOT use markdown.
        Do NOT wrap in ```json```.
        Return ONLY JSON:
        {{
        "executive_summary": "...",
        "recommendation": "PASS" or "FAIL"
        }}

        DATA:
        {context}
    """

    response = generate(prompt)

    try:
        result = json.loads(response)

        state["executive_summary"] = result["executive_summary"]
        state["recommendation"] = result["recommendation"]

    except Exception:
        state["executive_summary"] = "Failed to generate summary"
        state["recommendation"] = "FAIL"
    
    docx_path = render_docx(state)
    state["docx_path"] = docx_path

    pdf_path = convert_to_pdf(docx_path)
    filename = os.path.basename(pdf_path)

    state["pdf_path"] = f"http://127.0.0.1:8000/report/{filename}"

    return state