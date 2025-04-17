# Wine Intelligence Analysis App

A full-stack AI-powered wine analysis platform that combines expert-level sensory evaluation with real-time data aggregation. This app lets users input wine names or descriptions, intelligently extracts relevant information using Google Search and LLMs (Gemini), aggregates expert reviews and tasting notes from top wine websites, and analyzes the data using the WSET Systematic Approach to Tasting (SAT) criteria. Designed for wine enthusiasts, collectors, and professionals, it delivers a comprehensive SAT-style analysis, quality assessment, aging potential, and market price estimate—all in one place.

---

## Features

-  Text-based query understanding using Gemini
-  Smart wine query extraction using LLM (Gemini)
-  Google Programmable Search + Web crawling to collect wine data
-  File-based caching (search, HTML, LLM summaries)
-  SAT analysis aligned with WSET (Wine & Spirit Education Trust)
-  Gemini LLM integration for summary + evaluation
-  FastAPI-powered backend with Swagger UI
-  Model Context Protocol (MCP) schema for input-output traceability
-  Chat-style frontend powered by React, Next.js, Tailwind CSS
-  Docker + Makefile support for local development

---

## Project Structure

```
wine_ai_app/
├── app/
│   ├── api/                 # FastAPI routes
│   ├── analyzers/           # SAT scoring logic
│   ├── models/              # Pydantic schemas (MCP-based)
│   ├── services/            # LLM search, summarization, parsing
│   ├── utils/               # Caching, HTML parsing
│   └── main.py              # FastAPI app entry
├── cache/                   # File-based cache for APIs & scrapes
├── frontend/                # React/Next.js frontend
│   ├── src/components/      # UI components (ChatBox, ResultCard, etc.)
│   ├── pages/               # `/wine-intelligence-analysis` app
│   └── tailwind.config.js   # Tailwind styling
├── tests/                   # Pytest-based unit tests
├── .env                     # API keys and configs (only store at local)
├── Makefile                 # CLI shortcuts for dev + test
├── Dockerfile               # Containerized setup
├── docker-compose.yml       # Multi-service setup (optional)
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Local Development

### Backend (FastAPI + Gemini)

```bash
# 1. Clone the repo
git clone https://github.com/chenghwu/wine_ai_app.git && cd wine_ai_app

# 2. Create virtual environment and install dependencies
make install

# 3. Create a `.env` file at root with your keys
ENV=dev
GEMINI_API_KEY=your_google_gemini_key
GOOGLE_API_KEY=your_google_search_key
GOOGLE_CX=your_custom_search_engine_id
# Fill in your GEMINI_API_KEY and GOOGLE_API_KEY

# 6. Start the API
make run
```

Then visit [http://localhost:8000/swagger](http://localhost:8000/swagger) for Swagger UI.

---

### Frontend (Next.js UI)

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Then visit [http://localhost:3000/wine-intelligence-analysis](http://localhost:3000/wine-intelligence-analysis)

---

## Run Tests

```bash
make test

# or run a specific test, ex:
./venv/bin/pytest tests/test_llm_search_summary.py
```

---

## Docker Support (optional)

```bash
# Build and run locally in Docker
make docker-build
make docker-run

# Or full stack with docker-compose
make docker-compose-up
```

---

## Caching System

- Cached by SHA1 of query or content
- Used for: Google Search, HTML scraping, Gemini LLM
- Located under `/cache/{type}/{hash}.json`

---

## Next Steps

- Add PostgreSQL + Redis for persistence and caching
- Search and crawling improvement
- UI improvement
- Add wine label recognition (OCR)

---

## References

- [WSET Level 3 SAT](https://www.wsetglobal.com)
- Google Gemini API via `google.generativeai`
- Google Programmable Search
- Tailwind CSS + React + Next.js
