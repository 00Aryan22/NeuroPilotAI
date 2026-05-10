import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from utils.config import get_secret

load_dotenv()

MODEL_NAME = get_secret("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
ENABLE_CREWAI = str(get_secret("ENABLE_CREWAI", "false")).lower() in {"1", "true", "yes", "on"}
SYSTEM_PROMPT = (
    "You are NeuroPilot AI, an enterprise-grade autonomous assistant. "
    "Be concise, accurate, and provide structured outputs with actionability."
)

client = OpenAI(
    api_key=get_secret("OPENROUTER_API_KEY"),
    base_url=get_secret("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
)


def _chat(messages: List[Dict[str, str]], temperature: float = 0.4, max_tokens: int = 1200) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or "No response returned."


def ask_ai(question: str) -> str:
    try:
        return _chat(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.6,
            max_tokens=1000,
        )
    except Exception as exc:
        return f"AI request failed: {exc}"


def summarize_research(research_text: str) -> str:
    try:
        return _chat(
            [
                {"role": "system", "content": "Summarize into: key insights, trends, risks, and next actions."},
                {"role": "user", "content": research_text},
            ],
            temperature=0.35,
            max_tokens=900,
        )
    except Exception as exc:
        return f"Research summary failed: {exc}"


def analyze_github_repo(repo_data: str) -> str:
    try:
        return _chat(
            [
                {
                    "role": "system",
                    "content": (
                        "Act as a principal engineer. Analyze architecture, quality, scalability, risks, "
                        "and produce prioritized improvements."
                    ),
                },
                {"role": "user", "content": repo_data},
            ],
            temperature=0.35,
            max_tokens=1200,
        )
    except Exception as exc:
        return f"GitHub analysis failed: {exc}"


def answer_pdf_question(question: str, context: str) -> str:
    try:
        return _chat(
            [
                {
                    "role": "system",
                    "content": (
                        "Answer only from provided PDF excerpts. "
                        "If not present in context, say: 'I could not find that in the uploaded document.'"
                    ),
                },
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"},
            ],
            temperature=0.2,
            max_tokens=700,
        )
    except Exception as exc:
        return f"PDF question failed: {exc}"


def run_multi_agent_workflow(goal: str, research_summary: str = "", github_summary: str = "", pdf_summary: str = "") -> str:
    """
    Workflow orchestration with optional CrewAI mode.
    """
    prompt = (
        f"Goal: {goal}\n\nResearch:\n{research_summary}\n\nGitHub:\n{github_summary}\n\nPDF:\n{pdf_summary}\n\n"
        "Generate an autonomous execution plan with priorities, timeline, and risks."
    )

    # Cloud deployments are more reliable in direct LLM mode unless CrewAI is explicitly enabled.
    if not ENABLE_CREWAI:
        return ask_ai(prompt)

    try:
        from crewai import Agent, Crew, Task
    except Exception:
        return ask_ai(prompt)

    try:
        researcher = Agent(role="Research Agent", goal="Generate actionable research insights", backstory="Expert AI analyst")
        architect = Agent(role="GitHub Agent", goal="Evaluate repository engineering quality", backstory="Senior software architect")
        operator = Agent(role="Operations Agent", goal="Create implementation workflow", backstory="Startup CTO")

        tasks = [
            Task(
                description=f"Summarize priorities from this research context:\n{research_summary}",
                expected_output="Key insights and opportunities.",
                agent=researcher,
            ),
            Task(
                description=f"Extract architecture risks and improvements:\n{github_summary}",
                expected_output="Architecture analysis and engineering recommendations.",
                agent=architect,
            ),
            Task(
                description=(
                    f"Use goal: {goal}\nPDF notes:\n{pdf_summary}\n"
                    "Combine all inputs into a 5-step autonomous execution workflow."
                ),
                expected_output="Final combined execution plan.",
                agent=operator,
            ),
        ]

        crew = Crew(agents=[researcher, architect, operator], tasks=tasks, verbose=False)
        return str(crew.kickoff())
    except Exception as exc:
        return ask_ai(
            f"{prompt}\n\nCrewAI execution error for reference: {exc}\n"
            "Continue and produce the best final execution plan anyway."
        )