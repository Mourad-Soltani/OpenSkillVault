# OpenSkillVault - AI Agent Skills Manager
# Author: Mourad.Soltani
# Signature: Mourad.Soltani - 2026 Trending Project
"""OpenSkillVault Flask API — local-first AI Agent Skills Manager."""

from __future__ import annotations

import os
import sys

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AUTHOR, DATA_DIR, PROJECT, SIGNATURE, SKILLS_DIR, VERSION
from skills_manager import SkillsManager, _valid_id

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path="",
)
CORS(app)

os.makedirs(SKILLS_DIR, exist_ok=True)
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except OSError:
    pass

manager = SkillsManager(SKILLS_DIR)


def _err(message: str, status: int = 400):
    return jsonify({"error": message, "signature": SIGNATURE}), status


@app.route("/health")
def health():
    """Health check — production readiness. Mourad.Soltani"""
    return jsonify(
        {
            "status": "healthy",
            "project": PROJECT,
            "author": AUTHOR,
            "version": VERSION,
            "skills_count": manager.count(),
            "signature": SIGNATURE,
        }
    ), 200


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/skills", methods=["GET"])
def list_skills():
    category = request.args.get("category")
    q = request.args.get("q")
    skills = manager.list_skills(category=category, query=q)
    return jsonify(
        {
            "skills": skills,
            "count": len(skills),
            "author": AUTHOR,
            "signature": SIGNATURE,
        }
    )


@app.route("/api/skills/<skill_id>", methods=["GET"])
def get_skill(skill_id):
    if not _valid_id(skill_id):
        return _err("invalid skill id", 400)
    skill = manager.get_skill(skill_id)
    if not skill:
        return _err("Skill not found", 404)
    return jsonify(skill)


@app.route("/api/skills", methods=["POST"])
def create_skill():
    data = request.get_json(silent=True) or {}
    try:
        skill = manager.create_skill(data)
    except ValueError as e:
        return _err(str(e), 400)
    return jsonify(skill), 201


@app.route("/api/skills/<skill_id>", methods=["PUT"])
def update_skill(skill_id):
    if not _valid_id(skill_id):
        return _err("invalid skill id", 400)
    data = request.get_json(silent=True) or {}
    try:
        skill = manager.update_skill(skill_id, data)
    except ValueError as e:
        return _err(str(e), 400)
    if not skill:
        return _err("Skill not found", 404)
    return jsonify(skill)


@app.route("/api/skills/<skill_id>", methods=["DELETE"])
def delete_skill(skill_id):
    if not _valid_id(skill_id):
        return _err("invalid skill id", 400)
    if not manager.delete_skill(skill_id):
        return _err("Skill not found", 404)
    return jsonify({"deleted": True, "id": skill_id, "signature": SIGNATURE})


@app.route("/api/categories", methods=["GET"])
def categories():
    return jsonify(
        {"categories": manager.categories(), "signature": SIGNATURE}
    )


@app.route("/api/export", methods=["GET"])
def export_pack():
    return jsonify(manager.export_pack())


@app.route("/api/import", methods=["POST"])
def import_pack():
    data = request.get_json(silent=True) or {}
    overwrite = bool(data.get("overwrite", False))
    result = manager.import_pack(data, overwrite=overwrite)
    return jsonify(result), 200


@app.route("/api/stats", methods=["GET"])
def stats():
    return jsonify(
        {
            "project": PROJECT,
            "author": AUTHOR,
            "version": VERSION,
            "skills_count": manager.count(),
            "categories": manager.categories(),
            "signature": f"{SIGNATURE} — Built for the 2026 AI Agent Skills wave",
        }
    )


@app.errorhandler(404)
def not_found(_e):
    # SPA fallback for static assets already handled; API 404s stay JSON
    if request.path.startswith("/api/"):
        return _err("Not found", 404)
    return send_from_directory(app.static_folder, "index.html")


@app.errorhandler(500)
def server_error(_e):
    return _err("Internal server error", 500)


if __name__ == "__main__":
    print(f"Starting {PROJECT} by {AUTHOR} v{VERSION}")
    print(f"Signature: {SIGNATURE}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
