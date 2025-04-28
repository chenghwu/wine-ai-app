import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_search_wine_mock():
    os.environ["ENV"] = "dev"

    payload = {
        "input": {"query": "Opus One 2015"},
        "context": {
            "model": "gemini-2.0-flash",
            "user_id": "test-user",
            "timestamp": "2025-04-25T00:00:00",
            "ruleset": "WSET Level 4 SAT",
            "confidence": 0.9,
            "use_mock": True
        }
    }

    response = client.post("/api/chat-search-wine", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "mocked"
    assert "wine" in data["output"]