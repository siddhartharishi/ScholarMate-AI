import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List
from agents.config.states import ReportState


def normalize_arxiv_url(url: str) -> str:
    url = url.strip()

    # Raw ID → abs
    if not url.startswith("http"):
        url = f"https://arxiv.org/abs/{url}"

    # PDF → ABS
    if "/pdf/" in url:
        url = url.replace("/pdf/", "/abs/")

    # Remove .pdf
    if url.endswith(".pdf"):
        url = url[:-4]

    # Convert to ar5iv (ONLY ONCE)
    if "ar5iv.labs.arxiv.org" not in url:
        url = url.replace("arxiv.org", "ar5iv.labs.arxiv.org")

    return url


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return res.text
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch URL: {url}\n{e}")


def extract_title(soup: BeautifulSoup) -> str:
    # Best: ar5iv structured title
    title_tag = soup.find("h1", class_="ltx_title")
    if title_tag:
        return title_tag.get_text(" ", strip=True)

    # Fallback: HTML <title>
    if soup.title:
        title = soup.title.get_text(" ", strip=True)
        return title.replace("| ar5iv", "").strip()

    return "Unknown Title"


def extract_abstract(soup: BeautifulSoup) -> str:
    for selector in [
        ("div", "ltx_abstract"),
        ("p", "ltx_abstract"),
        ("blockquote", "abstract"),
    ]:
        tag = soup.find(selector[0], class_=selector[1])
        if tag:
            return tag.get_text(" ", strip=True)

    return "Abstract not found"


def clean_heading(text: str) -> str:
    text = re.sub(r"^\d+(\.\d+)*\s+", "", text)  # remove numbering
    return text.strip()


def clean_body(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_heading_from_body(raw_heading: str, body: str) -> str:
    if body.startswith(raw_heading):
        return body[len(raw_heading):].strip()
    return body



def extract_sections(soup: BeautifulSoup) -> List[Dict[str, str]]:
    sections = []

    for sec in soup.find_all("section"):
        heading_tag = sec.find(["h2", "h3"])
        if not heading_tag:
            continue

        raw_heading = heading_tag.get_text(" ", strip=True)
        heading = clean_heading(raw_heading)

        raw_body = sec.get_text(" ", strip=True)
        body = remove_heading_from_body(raw_heading, raw_body)
        body = clean_body(body)

        # Skip empty / tiny sections
        if len(body) < 50:
            continue

        sections.append({
            "heading": heading,
            "body": body
        })

    return sections


async def scrape_arxiv(state: ReportState) -> Dict[str, Any]:
    if "url" not in state or not state["url"]:
        raise ValueError("Missing 'url' in state")

    print("[SCRAPER] Input URL:", state["url"])

    url = normalize_arxiv_url(state["url"])
    print("[SCRAPER] Normalized URL:", url)

    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")


    title = extract_title(soup)
    abstract = extract_abstract(soup)
    sections = extract_sections(soup)


    if not sections:
        print("[SCRAPER WARNING] No structured sections found, fallback to body")

        body_text = soup.get_text(" ", strip=True)
        sections = [{
            "heading": "full_text",
            "body": clean_body(body_text[:20000])  # prevent overload
        }]

    state["title"] = title
    state["abstract"] = abstract
    state["sections"] = sections

    return state