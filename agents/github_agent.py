import base64
import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

from agents.ai_agent import analyze_github_repo

load_dotenv()


def _headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _extract_repo_slug(repo_input: str) -> str:
    cleaned = repo_input.strip().replace("https://github.com/", "").strip("/")
    return "/".join(cleaned.split("/")[:2])


def fetch_github_repo(repo_input: str) -> Dict[str, Any]:
    try:
        slug = _extract_repo_slug(repo_input)
        base_api = f"https://api.github.com/repos/{slug}"

        repo_res = requests.get(base_api, headers=_headers(), timeout=20)
        repo_res.raise_for_status()
        repo_data = repo_res.json()

        langs_res = requests.get(f"{base_api}/languages", headers=_headers(), timeout=20)
        languages = langs_res.json() if langs_res.ok else {}

        readme_res = requests.get(f"{base_api}/readme", headers=_headers(), timeout=20)
        readme_text = "README unavailable."
        if readme_res.ok:
            raw_content = readme_res.json().get("content", "")
            if raw_content:
                readme_text = base64.b64decode(raw_content).decode("utf-8", errors="ignore")

        combined_data = (
            f"Repository: {repo_data.get('full_name')}\n"
            f"Description: {repo_data.get('description')}\n"
            f"Stars: {repo_data.get('stargazers_count')}\n"
            f"Forks: {repo_data.get('forks_count')}\n"
            f"Open issues: {repo_data.get('open_issues_count')}\n"
            f"Primary language: {repo_data.get('language')}\n"
            f"Topics: {repo_data.get('topics')}\n"
            f"Languages map: {languages}\n"
            f"README excerpt:\n{readme_text[:12000]}"
        )
        analysis = analyze_github_repo(combined_data)
        return {"success": True, "analysis": analysis, "repo_data": repo_data, "languages": languages}
    except Exception as exc:
        return {"success": False, "analysis": f"GitHub fetch failed: {exc}", "repo_data": {}, "languages": {}}