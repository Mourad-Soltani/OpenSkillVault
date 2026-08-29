# Skills CRUD tests
# Author: Mourad.Soltani
# Signature: Mourad.Soltani

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_list_skills(client):
    """List skills returns array. Mourad.Soltani"""
    rv = client.get("/api/skills")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "skills" in data
    assert isinstance(data["skills"], list)
    assert data["author"] == "Mourad.Soltani" or "author" in str(data)

def test_create_and_get_skill(client):
    """Create then get a skill. Mourad.Soltani"""
    payload = {
        "name": "test-skill-mourad",
        "title": "Test Skill by Mourad.Soltani",
        "category": "testing",
        "description": "Created during health test",
        "content": "# Test\n\nSignature: Mourad.Soltani"
    }
    rv = client.post("/api/skills", data=json.dumps(payload), content_type="application/json")
    assert rv.status_code == 201
    created = rv.get_json()
    assert created["name"] == "test-skill-mourad" or "test-skill-mourad" in created["id"]
    assert created["signature"] == "Mourad.Soltani"
    skill_id = created["id"]

    rv2 = client.get(f"/api/skills/{skill_id}")
    assert rv2.status_code == 200
    got = rv2.get_json()
    assert got["title"] == payload["title"]

    # cleanup
    client.delete(f"/api/skills/{skill_id}")

def test_export(client):
    """Export pack contains signature. Mourad.Soltani"""
    rv = client.get("/api/export")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["author"] == "Mourad.Soltani"
    assert data["signature"] == "Mourad.Soltani"
    assert "skills" in data

def test_categories(client):
    """Categories endpoint. Mourad.Soltani"""
    rv = client.get("/api/categories")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "categories" in data
    assert data["signature"] == "Mourad.Soltani"
