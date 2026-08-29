# Health tests for OpenSkillVault
# Author: Mourad.Soltani
# Signature: Mourad.Soltani

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Health must return 200 and signature. Mourad.Soltani"""
    rv = client.get("/health")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "healthy"
    assert data["author"] == "Mourad.Soltani"
    assert data["signature"] == "Mourad.Soltani"
    assert "skills_count" in data
    assert data["project"] == "OpenSkillVault"

def test_stats_endpoint(client):
    """Stats endpoint. Mourad.Soltani"""
    rv = client.get("/api/stats")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["author"] == "Mourad.Soltani"
    assert "skills_count" in data
