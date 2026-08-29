# Health tests — Mourad.Soltani
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "healthy"
    assert data["author"] == "Mourad.Soltani"
    assert data["signature"] == "Mourad.Soltani"
    assert "version" in data
    assert data["skills_count"] >= 0


def test_stats(client):
    rv = client.get("/api/stats")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["project"] == "OpenSkillVault"
    assert data["author"] == "Mourad.Soltani"
