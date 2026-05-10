from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

from agents.ai_agent import answer_pdf_question, ask_ai, run_multi_agent_workflow
from agents.github_agent import fetch_github_repo
from agents.ppt_agent import generate_ppt
from agents.report_agent import generate_docx_report
from agents.research_agent import scrape_with_apify, web_research
from utils.pdf_parser import extract_text, save_uploaded_pdf
from utils.ui_helpers import glass_card, inject_css, section_title, timeline_chart, usage_chart
from utils.vector_store import VectorStoreManager

st.set_page_config(page_title="NeuroPilot AI", page_icon="🧠", layout="wide")
inject_css()


def init_state() -> None:
    defaults = {
        "session_id": str(uuid4())[:8],
        "research_history": [],
        "pdf_chat_history": [],
        "github_history": [],
        "workflow_history": [],
        "agent_status": {
            "Research Agent": "Idle",
            "PDF Agent": "Idle",
            "GitHub Agent": "Idle",
            "Report Agent": "Idle",
            "Presentation Agent": "Idle",
        },
        "pdf_loaded": False,
        "last_pdf_name": "",
        "last_research_summary": "",
        "last_github_summary": "",
        "last_pdf_summary": "",
        "last_report_path": "",
        "last_ppt_path": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_resource(show_spinner=False)
def get_vector_manager() -> VectorStoreManager:
    return VectorStoreManager()


init_state()
vector_manager = get_vector_manager()

with st.sidebar:
    st.markdown("## NeuroPilot AI")
    st.markdown('<span class="status-pill">System Online</span>', unsafe_allow_html=True)
    menu = st.radio(
        "Navigation",
        ["Dashboard", "Research Agent", "PDF RAG Chat", "GitHub Analyzer", "Autonomous Workflow", "Reports & PPT", "Analytics"],
    )
    st.caption(f"Session: `{st.session_state.session_id}`")

st.markdown(
    """
    <div class="hero">
        <h1>NeuroPilot AI</h1>
        <p>Autonomous Multi-Agent Research & Developer Operating System</p>
        <span class="status-pill"><span class="thinking-dot"></span>Live Agent Intelligence</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if menu == "Dashboard":
    section_title("Command Center", "Live intelligence and activity overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        glass_card("AI Agents", "5", "Autonomous crew enabled")
    with c2:
        glass_card("Research Queries", str(len(st.session_state.research_history)), "Tavily + LLM summaries")
    with c3:
        glass_card("PDF Q&A", str(len(st.session_state.pdf_chat_history)), "Chroma semantic retrieval")
    with c4:
        glass_card("GitHub Analyses", str(len(st.session_state.github_history)), "Architecture audits")

    st.markdown("### Agent Activity Monitor")
    left, right = st.columns(2)
    with left:
        for agent, status in st.session_state.agent_status.items():
            st.write(f"- **{agent}**: {status}")
    with right:
        st.code(
            "Input -> Research -> PDF RAG -> GitHub Audit -> Report -> PPT\n"
            "All workflows persist in session memory for quick iteration."
        )

elif menu == "Research Agent":
    section_title("AI Research Agent", "Live web intelligence with citations and summaries")
    query = st.text_area("Research Prompt", placeholder="Example: top enterprise AI coding trends in 2026")
    max_results = st.slider("Search Results", min_value=3, max_value=10, value=6)
    include_apify = st.checkbox("Enrich with Apify web scrape")

    if st.button("Run Live Research", use_container_width=True) and query.strip():
        st.session_state.agent_status["Research Agent"] = "Running"
        with st.spinner("Researching web sources..."):
            result = web_research(query, max_results=max_results)
            apify_rows = scrape_with_apify(result["raw_results"][0]["url"]) if include_apify and result["raw_results"] else []
            payload = {
                "query": query,
                "summary": result["summary"],
                "answer": result.get("answer", ""),
                "sources": result["raw_results"],
                "apify": apify_rows,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
            st.session_state.research_history.append(payload)
            st.session_state.last_research_summary = result["summary"]
            st.session_state.agent_status["Research Agent"] = "Completed"

    if st.session_state.research_history:
        latest = st.session_state.research_history[-1]
        st.success("Research workflow complete")
        st.markdown("#### AI Summary")
        st.write(latest["summary"])
        st.markdown("#### Sources")
        for source in latest["sources"][:6]:
            st.markdown(f"- [{source.get('title', 'Untitled')}]({source.get('url', '')})")

elif menu == "PDF RAG Chat":
    section_title("PDF RAG Chat", "Semantic retrieval + context-grounded answers")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded is not None:
        st.session_state.agent_status["PDF Agent"] = "Indexing"
        with st.spinner("Parsing and indexing PDF..."):
            file_path = save_uploaded_pdf(uploaded)
            text = extract_text(file_path)
            vector_manager.build_pdf_store(st.session_state.session_id, text)
            st.session_state.pdf_loaded = True
            st.session_state.last_pdf_name = uploaded.name
            st.session_state.last_pdf_summary = ask_ai(f"Summarize this document in 8 bullets:\n{text[:10000]}")
            st.session_state.agent_status["PDF Agent"] = "Ready"
        st.success(f"Indexed: {uploaded.name}")

    if st.session_state.pdf_loaded:
        st.caption(f"Active file: `{st.session_state.last_pdf_name}`")
        question = st.text_input("Ask from PDF knowledge base")
        if st.button("Ask NeuroPilot PDF", use_container_width=True) and question.strip():
            with st.spinner("Retrieving relevant chunks..."):
                db = vector_manager.load_pdf_store(st.session_state.session_id)
                docs = db.similarity_search(question, k=4)
                context = "\n\n".join(d.page_content for d in docs)
                answer = answer_pdf_question(question, context)
                st.session_state.pdf_chat_history.append({"question": question, "answer": answer, "time": datetime.now().isoformat()})
        for chat in st.session_state.pdf_chat_history[-5:][::-1]:
            st.markdown(f"**Q:** {chat['question']}")
            st.write(chat["answer"])
            st.markdown("---")

elif menu == "GitHub Analyzer":
    section_title("GitHub Repository Analyzer", "Architecture extraction and AI improvement recommendations")
    repo = st.text_input("GitHub URL or owner/repo", placeholder="https://github.com/streamlit/streamlit")
    if st.button("Analyze Repository", use_container_width=True) and repo.strip():
        st.session_state.agent_status["GitHub Agent"] = "Running"
        with st.spinner("Pulling repository metadata..."):
            result = fetch_github_repo(repo)
            st.session_state.github_history.append(result)
            st.session_state.last_github_summary = result["analysis"]
            st.session_state.agent_status["GitHub Agent"] = "Completed" if result["success"] else "Failed"

    if st.session_state.github_history:
        latest = st.session_state.github_history[-1]
        st.markdown("#### AI Repository Insight")
        st.write(latest["analysis"])
        if latest.get("repo_data"):
            rd = latest["repo_data"]
            cols = st.columns(3)
            cols[0].metric("Stars", rd.get("stargazers_count", 0))
            cols[1].metric("Forks", rd.get("forks_count", 0))
            cols[2].metric("Open Issues", rd.get("open_issues_count", 0))

elif menu == "Autonomous Workflow":
    section_title("Autonomous Multi-Agent OS", "CrewAI collaborative execution across all agents")
    goal = st.text_area("Workflow Goal", placeholder="Build launch strategy for AI developer platform")
    if st.button("Run Autonomous Workflow", use_container_width=True) and goal.strip():
        with st.spinner("Agents collaborating..."):
            workflow_output = run_multi_agent_workflow(
                goal=goal,
                research_summary=st.session_state.last_research_summary,
                github_summary=st.session_state.last_github_summary,
                pdf_summary=st.session_state.last_pdf_summary,
            )
            st.session_state.workflow_history.append({"goal": goal, "output": workflow_output, "time": datetime.now().isoformat()})
        st.success("Workflow complete")

    if st.session_state.workflow_history:
        st.markdown("#### Latest Workflow Output")
        st.write(st.session_state.workflow_history[-1]["output"])

elif menu == "Reports & PPT":
    section_title("AI Report and Presentation Studio", "Generate pitch-ready assets instantly")
    report_title = st.text_input("Report Title", value="NeuroPilot AI Intelligence Brief")
    if st.button("Generate DOCX Report", use_container_width=True):
        st.session_state.agent_status["Report Agent"] = "Running"
        path = generate_docx_report(
            title=report_title,
            sections={
                "Research Summary": st.session_state.last_research_summary or "No research generated yet.",
                "GitHub Analysis": st.session_state.last_github_summary or "No repository analyzed yet.",
                "PDF Insights": st.session_state.last_pdf_summary or "No PDF loaded yet.",
                "Workflow Output": st.session_state.workflow_history[-1]["output"] if st.session_state.workflow_history else "No autonomous workflow yet.",
            },
        )
        st.session_state.last_report_path = path
        st.session_state.agent_status["Report Agent"] = "Completed"
        st.success(f"Report generated: {path}")

    if st.button("Generate PPT Deck", use_container_width=True):
        st.session_state.agent_status["Presentation Agent"] = "Running"
        ppt_path = generate_ppt(
            title="NeuroPilot AI Deck",
            sections={
                "Market Signals": st.session_state.last_research_summary or "Research pending",
                "Product Architecture": st.session_state.last_github_summary or "GitHub analysis pending",
                "Document Intelligence": st.session_state.last_pdf_summary or "PDF summary pending",
                "Execution Plan": st.session_state.workflow_history[-1]["output"] if st.session_state.workflow_history else "Workflow pending",
            },
        )
        st.session_state.last_ppt_path = ppt_path
        st.session_state.agent_status["Presentation Agent"] = "Completed"
        st.success(f"Presentation generated: {ppt_path}")

    report_path = st.session_state.last_report_path
    if report_path and Path(report_path).exists():
        with open(report_path, "rb") as report_file:
            st.download_button(
                "Download DOCX Report",
                data=report_file.read(),
                file_name=Path(report_path).name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )

    ppt_path = st.session_state.last_ppt_path
    if ppt_path and Path(ppt_path).exists():
        with open(ppt_path, "rb") as ppt_file:
            st.download_button(
                "Download PPT Deck",
                data=ppt_file.read(),
                file_name=Path(ppt_path).name,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
            )

elif menu == "Analytics":
    section_title("Operational Analytics", "Usage telemetry, workflow activity, and system behavior")
    metrics = {
        "Research": len(st.session_state.research_history),
        "PDF Chats": len(st.session_state.pdf_chat_history),
        "GitHub Analyses": len(st.session_state.github_history),
        "Workflows": len(st.session_state.workflow_history),
    }
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(usage_chart(metrics), use_container_width=True)
    with c2:
        timeline = [{"event": key, "count": value} for key, value in metrics.items()]
        st.plotly_chart(timeline_chart(timeline), use_container_width=True)

    st.markdown("#### Live Agent Status")
    for agent, status in st.session_state.agent_status.items():
        st.write(f"- `{agent}` -> **{status}**")