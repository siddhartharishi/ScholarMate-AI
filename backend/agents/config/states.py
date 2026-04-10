from typing import TypedDict, List


class FactCheckState(TypedDict):
    claim: str
    verified: bool


class ReportState(TypedDict):
    url: str
    paper_id: str
    title: str
    abstract: str
    sections: list

    consistency_score: int
    grammar_rating: str
    novelty: str
    fact_check: List[FactCheckState]

    authenticity_score: int

    executive_summary: str
    recommendation: str

    pdf_path: str