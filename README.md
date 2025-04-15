# 🍷 Wine Analysis App

An AI-driven FastAPI backend that evaluates wine quality using the WSET Level 3 SAT (Systematic Approach to Tasting) and wraps each analysis using the Model Context Protocol (MCP). This project is structured for containerized deployment and designed for extensibility with critic ratings, label recognition, and market price data.

---

## Features

- FastAPI-powered backend with Swagger UI
- Model Context Protocol (MCP) schema for input-output traceability
- Dockerized and production-deployable
- Modular codebase (routes, services, models, utils)
- SAT scoring engine based on WSET Level 3 (BLIC: Balance, Length, Intensity, Complexity)

---

## Project Structure

```
wine_ai_app/
├── app/
│   ├── main.py               # FastAPI entrypoint
│   ├── api/routes.py         # API routes
│   ├── models/mcp_model.py   # MCP schema: input/output/context
│   ├── services/analyzer.py  # SAT scoring engine
│   └── utils/logger.py       # Placeholder for logging setup
├── requirements.txt          # Project dependencies
├── Dockerfile                # Docker config for containerization
└── README.md                 # Project documentation
```

---

## Setup

### Run Locally

```bash
# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
./venv/bin/pip install -r requirements.txt

# Run FastAPI
uvicorn app.main:app --reload
```

Swagger UI: [http://localhost:8000/swagger](http://localhost:8000/swagger)

---

## Sample Request

**POST** `/api/analyze`

```json
{
  "input": {
    "appearance": {
      "clarity": "clear",
      "intensity": "deep",
      "color": "ruby"
    },
    "nose": {
      "intensity": "pronounced",
      "aromas": ["blackberry", "vanilla", "cedar"]
    },
    "palate": {
      "acidity": "high",
      "tannin": "medium+",
      "body": "full",
      "finish": "long",
      "intensity": "pronounced",
      "flavors": ["blackberry", "vanilla", "spice", "oak"]
    }
  },
  "output": {},
  "context": {
    "model": "sat-v1",
    "timestamp": "2025-04-15T14:00:00Z",
    "confidence": 0.93,
    "user_id": "user1",
    "ruleset": "WSET Level 3 SAT"
  }
}
```

---

## Docker

Build and run the Docker container:

```bash
docker build -t wine-ai-app .
docker run -p 8000:8000 wine-ai-app
```

---

## Next Steps

- Add wine label recognition (YOLOv8 or Google Cloud Vision)
- Integrate expert critic reviews + market price APIs
- Enhance SAT logic
- Add PostgreSQL + Redis for persistence and caching
