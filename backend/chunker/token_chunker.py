import random
from agents.config.states import ReportState


def build_full_text(state: ReportState) -> str:
    text_parts = []

    # Add title + abstract
    if state.get("title"):
        text_parts.append(state["title"])

    if state.get("abstract"):
        text_parts.append(state["abstract"])

    # not considering reference section for grammar check
    skip_sections = ["reference", "bibliography", "acknowledgement"]

    for sec in state.get("sections", []):
        heading = sec.get("heading", "").lower()
        body = sec.get("body", "")

        if any(skip in heading for skip in skip_sections):
            continue

        if heading:
            text_parts.append(heading)

        if body:
            text_parts.append(body)

    return "\n\n".join(text_parts)

def sample_chunks(text: str, num_chunks=5, chunk_size=3000) -> str:
    if len(text) <= chunk_size:
        return text

    chunks = []
    max_start = max(len(text) - chunk_size, 1)

    for _ in range(num_chunks):
        start = random.randint(0, max_start)
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)

    return "\n\n".join(chunks)

def combine_text(state: ReportState) -> str:
    full_text = build_full_text(state)
    sampled_text = sample_chunks(full_text, num_chunks=5, chunk_size=3000)
    return sampled_text

