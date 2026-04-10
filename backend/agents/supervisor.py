import asyncio
import os, uuid
from dotenv import load_dotenv
load_dotenv()
from langgraph.graph import StateGraph, END

from agents.grammar_agent import grammar_check_agent
from agents.consistency_agent import consistency_agent
from agents.fact_check_agent import fact_check_agent
from agents.authenticity_agent import authenticity_agent
from agents.novelty_agent import novelty_agent
from report.synthesizer import synthesizer_agent
from scraper.arxiv_scraper import scrape_arxiv


from agents.config.states import ReportState

async def base_node(state: ReportState) -> ReportState:

    return await scrape_arxiv(state)

     

async def parallel_agents_node(state: ReportState) -> ReportState:

    async def run_all():
        results = await asyncio.gather(
            asyncio.to_thread(grammar_check_agent, state),
            asyncio.to_thread(consistency_agent, state),
            asyncio.to_thread(fact_check_agent, state),
            asyncio.to_thread(authenticity_agent, state),
            asyncio.to_thread(novelty_agent, state),
        )
        return results

    results = await run_all()

    # Merge results safely
    for res in results:
        state.update(res)

    # print("state in prallel_node: ", results)
    return state


def synthesizer_node(state: ReportState) -> ReportState:
    return synthesizer_agent(state)



def build_graph():
    builder = StateGraph(ReportState)

    # Nodes
    builder.add_node("base", base_node)
    builder.add_node("parallel", parallel_agents_node)
    builder.add_node("synthesizer", synthesizer_node)

    # Flow
    builder.set_entry_point("base")
    builder.add_edge("base", "parallel")
    builder.add_edge("parallel", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder.compile()



async def run_pipeline(url: str):

    graph = build_graph()
    session_id= str(uuid.uuid4())
    initial_state: ReportState = {
        "url": url,
        "paper_id": f"paper_{session_id[:6]}",
        "title": "",
        "abstract": "",
        "sections": [],

        "consistency_score": 0,

        "grammar_rating": "",
        "novelty": "",
        "fact_check": [],

        "authenticity_score": 0,

        "executive_summary": "",
        "recommendation": ""
    }

    result = await graph.ainvoke(initial_state)
    return result



if __name__ == "__main__":
    url = input("Enter arXiv URL: ").strip()

    final_state = asyncio.run(run_pipeline(url))

    print("\n--- FINAL REPORT ---\n")
    print("paper ID:", final_state["paper_id"])
    print("Title:", final_state["title"])
    print("Grammar:", final_state["grammar_rating"])
    print("Consistency:", final_state["consistency_score"])
    print("Authenticity:", final_state["authenticity_score"])

    print("\nNovelty:\n", final_state["novelty"])
    print("\nFact Check:", final_state["fact_check"])

    print("\nExecutive Summary:\n", final_state["executive_summary"])
    print("\nRecommendation:", final_state["recommendation"])