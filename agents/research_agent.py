import os
from typing import Any, Dict, List

from apify_client import ApifyClient
from dotenv import load_dotenv
from tavily import TavilyClient

from agents.ai_agent import summarize_research
from utils.config import get_secret

load_dotenv()

tavily_client = TavilyClient(api_key=get_secret("TAVILY_API_KEY"))


def web_research(query: str, max_results: int = 6) -> Dict[str, Any]:
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True,
        )
        results = response.get("results", [])
        context = "\n\n".join(
            [
                f"Title: {item.get('title', '')}\nURL: {item.get('url', '')}\nSnippet: {item.get('content', '')}"
                for item in results
            ]
        )
        summary = summarize_research(context) if context else "No relevant results were found."
        return {"summary": summary, "raw_results": results, "answer": response.get("answer", "")}
    except Exception as exc:
        return {"summary": f"Research failed: {exc}", "raw_results": [], "answer": ""}


def scrape_with_apify(url: str) -> List[Dict[str, Any]]:
    token = get_secret("APIFY_API_TOKEN")
    if not token:
        return [{"error": "APIFY_API_TOKEN is not configured."}]
    try:
        client = ApifyClient(token)
        run_input = {
            "startUrls": [{"url": url}],
            "maxCrawlDepth": 1,
            "maxCrawlPages": 3,
        }
        run = client.actor("apify/website-content-crawler").call(run_input=run_input)
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
        return dataset_items[:8]
    except Exception as exc:
        return [{"error": f"Apify scrape failed: {exc}"}]