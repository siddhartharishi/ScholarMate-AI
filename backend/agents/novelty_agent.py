import json, os, requests
from dotenv import load_dotenv
from typing import TypedDict, List
from agents.config.llm import generate
from agents.config.states import ReportState
from langsmith import traceable
load_dotenv()


def combine_text(state: ReportState) -> str:
    text = ""

    # for paper in state["base_report"]:
    text += state.get("title", "") + "\n\n"
    text += state.get("abstract", "") + "\n\n"

    return text


def generate_summary(text: str) -> str:
    prompt = f"""
Summarize what is NOVEL in this research paper.

Focus on:
- new idea
- methodology
- improvement over prior work
- unique contribution

Return only concise summary.

TEXT:
{text}
"""
    response = generate(prompt)
    return response.strip()

def search_papers(query: str):
    url = "https://serpapi.com/search"

    params = {
        "q": query,
        "api_key": os.getenv("SERPAPI_KEY"),
        "num": 3
    }

    res = requests.get(url, params=params)
    data = res.json()
    return data.get("data", [])



def evaluate_novelty(summary: str, papers: list) -> str:
    context = ""

    for p in papers:
        context += f"""
            TITLE: {p.get('title')}
            YEAR: {p.get('year')}
            ABSTRACT: {p.get('abstract')}
            """

    prompt = f"""
        You are a research evaluator.

        Given:
        1. A paper's novelty summary
        2. Related prior work

        Evaluate if the paper is truly novel.

        Consider:
        - publication year
        - methodology differences
        - use-case improvements
        - originality

        Return a qualitative explanation:

        SUMMARY:
        {summary}

        RELATED WORK:
        {context}
    """

    response = generate(prompt)
    return response



@traceable(name="novelty_agent")
def novelty_agent(state: ReportState) -> ReportState:
    text = combine_text(state)

    # Step 1: Summarize novelty
    summary = generate_summary(text)

    # Step 2: Store locally (simple KB)
    with open("novelty_kb.txt", "a") as f:
        f.write(summary + "\n\n")

    # Step 3: Retrieve related work
    papers = search_papers(summary)

    # Step 4: Evaluate novelty
    explanation = evaluate_novelty(summary, papers)

    # Step 5: Update state
    state["novelty"] = explanation
    
    return state