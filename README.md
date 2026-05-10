# NeuroPilot AI

Autonomous Multi-Agent Research & Developer Operating System built for hackathon-grade demos and startup-ready execution.

## Why NeuroPilot AI

NeuroPilot AI combines live research, repo intelligence, PDF RAG, autonomous planning, and report/presentation generation in one premium Streamlit platform optimized for low-spec laptops.

## Core Capabilities

- Live AI web research with Tavily (+ optional Apify enrichment)
- GitHub repository architecture analyzer with AI recommendations
- PDF semantic chat using Chroma vector memory
- Multi-agent workflow orchestration via CrewAI (with fallback mode)
- AI-generated DOCX reports and PPT slides
- Dynamic analytics dashboard and persistent session memory
- Futuristic glassmorphism/neon startup UI

## Tech Stack

- **Frontend:** Streamlit + custom CSS animations
- **Backend:** Python 3.11 modular services
- **Models:** OpenRouter (`openai/gpt-3.5-turbo` default)
- **Agent Frameworks:** CrewAI + LangChain ecosystem
- **Research:** Tavily API + Apify
- **RAG:** pypdf + ChromaDB + OpenAI embeddings
- **Outputs:** python-docx + python-pptx
- **Analytics:** Plotly

## Project Structure

```text
NeuroPilotAI/
├── app.py
├── requirements.txt
├── README.md
├── .env
├── agents/
│   ├── ai_agent.py
│   ├── research_agent.py
│   ├── github_agent.py
│   ├── report_agent.py
│   └── ppt_agent.py
├── utils/
│   ├── pdf_parser.py
│   ├── vector_store.py
│   └── ui_helpers.py
├── styles/
│   └── main.css
├── uploads/
├── reports/
├── presentations/
└── vector_db/
```

## Setup Guide

1. Create and activate virtual environment:
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Configure `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=openai/gpt-3.5-turbo
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
TAVILY_API_KEY=your_tavily_key
APIFY_API_TOKEN=your_apify_token
GITHUB_TOKEN=optional_github_token_for_higher_rate_limits
```

4. Run app:
   - `streamlit run app.py`

## Deployment Guide

### Streamlit Community Cloud

1. Push project to GitHub.
2. In Streamlit Cloud, choose repo + branch.
3. Set app entry point to `app.py`.
4. Add environment variables in Streamlit secrets.
5. Deploy.

### Render / VM Deployment

- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Performance Notes (8GB RAM / No GPU)

- Uses API-based models only (no local LLM loading)
- Chroma persists vectors to disk (`vector_db/`) to avoid reprocessing
- Streamlit session state keeps app memory lightweight and stable
- Cached vector manager avoids repeated initialization overhead
- Lightweight CSS animations avoid heavy frontend rendering cost

## Hackathon Demo Flow

1. Run **Research Agent** on a trending topic.
2. Upload a PDF in **PDF RAG Chat** and ask insight questions.
3. Analyze a repository in **GitHub Analyzer**.
4. Generate an autonomous plan in **Autonomous Workflow**.
5. Export deliverables in **Reports & PPT**.
6. Present impact using **Analytics**.
