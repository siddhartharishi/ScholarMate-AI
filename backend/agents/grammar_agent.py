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

    prompt = f"""
        You are an expert academic writing reviewer.
        Your task is to evaluate the grammar and writing quality of a research paper.

        Focus on:
        - Clarity of sentences
        - Correct grammar usage
        - Appropriate academic tone
        - Sentence structure 
        - Use of precise technical language
        - Avoidance of unnecessary repetition or vague wording

        Do NOT evaluate the research quality — only the writing.
        Rate the grammar quality as ONE of:
        - "high" - clear, precise, well-structured academic writing with minimal issues
        - "medium" - generally understandable but contains noticeable grammar issues, awkward phrasing, or inconsistency
        - "low" - poor grammar, unclear sentences, frequent errors, or difficult to read

        Text to evaluate:
        {text}

        Do NOT use markdown.
        Do NOT wrap in ```json```.
        Return ONLY JSON:
        {{
            "grammar_rating": "medium" | "low" | "high"
        }}
    """

    response = generate(prompt)
    try:
        result = json.loads(response)
        rating = result.get("grammar_rating", "medium").lower()

        if rating not in ["high", "medium", "low"]:
            rating = "medium"

        state["grammar_rating"] = rating

    except Exception:
        state["grammar_rating"] = "medium"

    return state
