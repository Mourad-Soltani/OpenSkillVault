# Skills CRUD tests — Mourad.Soltani
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_list_skills(client):
    rv = client.get("/api/skills")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "skills" in data
    assert isinstance(data["skills"], list)
    assert data.get("signature") == "Mourad.Soltani" or data.get("author") == "Mourad.Soltani"


def test_create_get_update_delete(client):
    payload = {
        "name": "test-skill-mourad",
        "title": "Test Skill by Mourad.Soltani",
        "category": "testing",
        "description": "Created during health test",
        "tags": ["test"],
        "content": "# Test\n\nSignature: Mourad.Soltani",
    }
    rv = client.post("/api/skills", data=json.dumps(payload), content_type="application/json")
    assert rv.status_code == 201
    created = rv.get_json()
    assert "test-skill-mourad" in created["id"]
    assert created["signature"] == "Mourad.Soltani"
    skill_id = created["id"]

    rv2 = client.get(f"/api/skills/{skill_id}")
    assert rv2.status_code == 200
    assert rv2.get_json()["title"] == payload["title"]

    rv3 = client.put(
        f"/api/skills/{skill_id}",
        data=json.dumps({"title": "Updated Title", "content": "# Updated"}),
        content_type="application/json",
    )
    assert rv3.status_code == 200
    assert rv3.get_json()["title"] == "Updated Title"

    # path traversal rejected
    rv_bad = client.get("/api/skills/../etc/passwd")
    assert rv_bad.status_code in (400, 404)

    rv4 = client.delete(f"/api/skills/{skill_id}")
    assert rv4.status_code == 200
    assert client.get(f"/api/skills/{skill_id}").status_code == 404


def test_validation_name_required(client):
    rv = client.post("/api/skills", data=json.dumps({}), content_type="application/json")
    assert rv.status_code == 400


def test_export_import(client):
    rv = client.get("/api/export")
    assert rv.status_code == 200
    pack = rv.get_json()
    assert pack["author"] == "Mourad.Soltani"
    assert pack["signature"] == "Mourad.Soltani"
    assert "skills" in pack

    rv2 = client.post(
        "/api/import",
        data=json.dumps({"skills": [], "overwrite": False}),
        content_type="application/json",
    )
    assert rv2.status_code == 200
    assert "created" in rv2.get_json()


def test_categories_and_search(client):
    assert client.get("/api/categories").status_code == 200
    rv = client.get("/api/skills?q=review")
    assert rv.status_code == 200
