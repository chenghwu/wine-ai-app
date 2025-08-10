# 🍷 Wine Intelligence Analysis App

A full-stack AI-powered wine analysis platform that combines expert-level sensory evaluation with real-time data aggregation. This app lets users input wine names or descriptions, intelligently extracts relevant information using Google Search and LLMs (Gemini), aggregates expert reviews and tasting notes from top wine websites, and analyzes the data using the WSET Systematic Approach to Tasting (SAT) criteria. Designed for wine enthusiasts, collectors, and professionals, it delivers a comprehensive SAT-style analysis, quality assessment, aging potential, and market price estimate—all in one place.

---

## ⭐️ Features

### 🍷 Wine Analysis Mode
-  **Dual Search Methods**: Text input OR camera/photo wine label recognition
-  **OCR Wine Label Analysis**: Capture wine labels via camera or upload photos for automatic wine information extraction
-  Text-based query understanding using Gemini
-  Smart wine query extraction using LLM (Gemini)
-  Google Programmable Search + Web crawling to collect wine data
-  SAT analysis aligned with WSET (Wine & Spirit Education Trust)
-  **Food Pairing Recommendations**: AI-powered wine-to-food pairing suggestions

### 🍽️ Menu Analysis Mode
-  **Menu-to-Wine Pairing**: Upload menu photos or describe dishes to get wine recommendations
-  **OCR Menu Processing**: Extract menu items from restaurant menu photos
-  **Specific Wine Recommendations**: Get targeted wine suggestions for each dish
-  **General Wine Categories**: Receive wine style and varietal guidance for menu items

### 🎯 Core Features
-  **Dual-Mode Interface**: Toggle between Wine Mode and Menu Mode workflows
-  **Session-based Search History**: Track and restore previous searches with dropdown interface
-  File-based caching (search, HTML, LLM summaries)
-  Gemini LLM integration for summary + evaluation
-  Chat-style frontend powered by React, Next.js, Tailwind CSS
-  **Real-time Progress Tracking**: Detailed analysis stages with progress indicators
-  Docker + Makefile support for local development

---

## 🖥️ Tech Stack

### Frontend
- **React** via **Next.js 15+ (App Router)**
- TypeScript
- **Tailwind CSS** for utility-first styling
- Deployed on **Firebase Hosting**

### Backend
- **FastAPI** (Python 3.11)
- **Gemini LLM** via MCP API
- **Gemini Vision API** for OCR and image analysis
- **Google Programmable Search API**
- **Image Processing** with Pillow (PIL) for OCR optimization
- **File-based and PostgreSQL caching**
- Deployed on **Google Cloud Run**

### Database
- **PostgreSQL** (schema-migrated via Alembic)
- Local: Dockerized
- Cloud: PostgreSQL (hosted on Neon)

### DevOps / Infrastructure
- **Docker** & **Docker Compose** for local development
- `Makefile` to simplify startup (`make docker-compose-up`)
- `.env` configuration for secrets + runtime toggles
- Environment-based mock response engine
- Service health monitored by **UptimeRobot**

---

## ⚙️  Project Structure

```
wine_ai_app/
├── app/                   # FastAPI backend
│   ├── api/               # API routes
│   ├── db/                # Database interactions
│   │   ├── crud/          # CRUD database operations
│   │   ├── models/        # SQLAlchemy models
│   │   └── session.py     # DB session management
│   ├── models/            # Pydantic models for request/response
│   ├── prompts/           # LLM prompt templates
│   ├── services/          # Business logic (LLM, rules, handlers, image processing)
│   │   ├── image/         # Image validation and processing
│   │   ├── vision/        # Gemini Vision API integration
│   │   └── handlers/      # Request handlers including image analysis
│   ├── scripts/           # Utility and maintenance scripts
│   ├── utils/             # Common utilities (caching, env, search)
│   ├── config.py          # Application configuration
│   ├── exceptions.py      # Custom exceptions
│   ├── main.py            # FastAPI application entry point
│   └── version.py         # Application version
│
├── frontend/              # Next.js frontend (App Router)
│   ├── src/components/    # SearchInput, ResultCard, ProgressIndicator, InlineCameraCapture
│   ├── src/types/         # TypeScript type definitions and progress messages
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
- Node.js 20+
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

### Frontend (Firebase Hosting)
The frontend is deployed to Firebase Hosting using GitHub Actions:
- CI/CD pipeline triggered on pushes to `main` and `dev` branches.
- `main` branch deploys to the production Firebase Hosting site.
- `dev` branch deploys to a separate development Firebase Hosting site.
- Node.js 20.x is used for building the Next.js application.
- Firebase CLI (`firebase-tools`) is used for deployment.
- Environment variables (`NEXT_PUBLIC_API_URL`, etc.) are configured during the build step in GitHub Actions.

### Backend (Google Cloud Run)
The FastAPI backend is deployed to Google Cloud Run using GitHub Actions:
- CI/CD pipeline triggered on pushes to `main` and `dev` branches.
- Docker images are built using Google Cloud Build and pushed to Google Artifact Registry.
  - `main` branch images are tagged `latest` for the production service (`wine-api`).
  - `dev` branch images are tagged `dev` for the development service (`wine-api-dev`).
- Environment variables are managed using `.env` files (converted to `env.yaml` by `scripts/convert_env_to_yaml.py`) and applied during Cloud Run deployment.
- The service runs on a managed platform with 1 CPU and 1Gi memory.
- For local development, a PostgreSQL database can be run via Docker Compose (`make docker-compose-up`), mirroring the cloud setup which connects to a PostgreSQL instance hosted on Neon.

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

- Search and crawling improvement
- UI improvement
- Enhance OCR accuracy with additional image preprocessing
- 

---

## 📘 References

- [WSET Level 3 SAT](https://www.wsetglobal.com)
- Google Gemini API via `google.generativeai`
- Google Programmable Search
- Tailwind CSS + React + Next.js
