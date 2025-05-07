# 🍷 Wine Intelligence Analysis App

A full-stack AI-powered wine analysis platform that combines expert-level sensory evaluation with real-time data aggregation. This app lets users input wine names or descriptions, intelligently extracts relevant information using Google Search and LLMs (Gemini), aggregates expert reviews and tasting notes from top wine websites, and analyzes the data using the WSET Systematic Approach to Tasting (SAT) criteria. Designed for wine enthusiasts, collectors, and professionals, it delivers a comprehensive SAT-style analysis, quality assessment, aging potential, and market price estimate—all in one place.

---

## ⭐️ Features

-  Text-based query understanding using Gemini
-  Smart wine query extraction using LLM (Gemini)
-  Google Programmable Search + Web crawling to collect wine data
-  File-based caching (search, HTML, LLM summaries)
-  Gemini LLM integration for summary + evaluation
-  SAT analysis aligned with WSET (Wine & Spirit Education Trust)
-  Chat-style frontend powered by React, Next.js, Tailwind CSS
-  Docker + Makefile support for local development

---

## 🖥️ Tech Stack

### Frontend
- **React** via **Next.js (App Router)**
- TypeScript
- **Tailwind CSS** for utility-first styling
- Deployed on **Vercel**

### Backend
- **FastAPI** (Python 3.11)
- **Gemini LLM** via MCP API
- **Google Programmable Search API**
- **File-based and PostgreSQL caching**
- Deployed on **Render**

### Database
- **PostgreSQL** (schema-migrated via Alembic)
- Local: Dockerized
- Cloud: Render PostgreSQL instance

### DevOps / Infrastructure
- **Docker** & **Docker Compose** for local development
- `Makefile` to simplify startup (`make docker-compose-up`)
- `.env` configuration for secrets + runtime toggles
- Environment-based mock response engine

---

## ⚙️  Project Structure

```
wine_ai_app/
├── app/                   # FastAPI backend
│   ├── api/               # Routes
│   ├── db/                # DB models, session, init
│   ├── services/          # LLM, rules, handlers
│   ├── models/            # MCP request models
│   ├── prompts/           # LLM prompts
│   └── utils/             # Caching, env, search
│
├── frontend/              # Next.js frontend (App Router)
│   ├── src/components/    # SearchInput, ResultCard, etc.
│   ├── src/app/           # Main page layout
│   └── public/            # Static assets
│
├── tests/                 # Pytest integration tests
├── alembic/               # DB migration scripts
├── cache/                 # HTML/search/summary file cache
├── Dockerfile             # Backend Dockerfile
├── docker-compose.yml     # API + DB orchestration
├── .env                   # API keys and configs (only store at local)
├── Makefile               # Dev commands
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 💻 Running Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for DB + backend)
- `.env` and `.env.local` for API keys/config

### Backend (FastAPI + Gemini)

1. Clone the repo
```bash
git clone https://github.com/chenghwu/wine_ai_app.git && cd wine_ai_app
```

2. Create `.env` file at root with your keys and environment variables
```bash
ENV=dev
GEMINI_API_KEY=your_google_gemini_key
GOOGLE_API_KEY=your_google_search_key
GOOGLE_CX=your_custom_search_engine_id
# Fill in your GEMINI_API_KEY and GOOGLE_API_KEY
```

3. Run backend and DB
```bash
make docker-compose-up  # starts backend + PostgreSQL
# OR for development only
make install
make init-db
make run
```

Then visit [http://localhost:8080/swagger](http://localhost:8080/swagger) for Swagger UI.

### Frontend (Next.js UI)

In a new terminal

1. At fronend directory, create `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8080/api
NEXT_PUBLIC_SHOW_MOCK_TOGGLE=true
```

2. Run 
```bash
cd frontend
npm install     # Install dependencies
npm run dev     # Start dev server
```

Then visit [http://localhost:3000](http://localhost:3000)

---

## 🧪 Run Tests

```bash
make test

# or run a specific test, ex:
./venv/bin/pytest tests/test_llm_search_summary.py
```

---

## 🚀 Deployment

### Frontend (Vercel)
Frontend is deployed to Vercel using:
- Auto-deployment from GitHub
- Vercel environment variables (`NEXT_PUBLIC_API_URL`, etc.)
- `frontend/` as root, using default build settings

### Backend (Render)
FastAPI backend is deployed on Render:
- `Dockerfile`-based deployment
- Environment variables configured in Render Dashboard
- PostgreSQL and `make docker-compose-up` for local mirroring

---

## 🐳 Docker Support (optional)

```bash
# Build and run locally in Docker
make docker-build
make docker-run

# Or full stack with docker-compose
make docker-compose-up
```

---

## ⚡️ Caching System

- Cached by SHA1 of query or content
- Used for: Google Search, HTML scraping, Gemini LLM
- Located under `/cache/{type}/{hash}.json`

---

## 💡 Next Steps

- Add Redis for persistence and caching
- Search and crawling improvement
- UI improvement
- Add wine label recognition (OCR)

---

## 📘 References

- [WSET Level 3 SAT](https://www.wsetglobal.com)
- Google Gemini API via `google.generativeai`
- Google Programmable Search
- Tailwind CSS + React + Next.js
