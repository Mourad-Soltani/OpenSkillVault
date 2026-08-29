# OpenSkillVault - AI Agent Skills Manager
# Author: Mourad.Soltani
# Signature: Mourad.Soltani - 2026 Trending Project
"""
OpenSkillVault - Local-first AI Agent Skills Manager
Inspired by 2026 GitHub trending: skills packs, taste-skill, agent harnesses.
"""

from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import os
import sys

# Mourad.Soltani signature block
AUTHOR = "Mourad.Soltani"
PROJECT = "OpenSkillVault"
VERSION = "1.0.0"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills_manager import SkillsManager

app = Flask(__name__, 
            static_folder="../frontend", 
            template_folder="../templates")
CORS(app)

# Data paths - Mourad.Soltani
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(SKILLS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

manager = SkillsManager(SKILLS_DIR)

@app.route("/health")
def health():
    """Health check endpoint - required for production readiness. Mourad.Soltani"""
    return jsonify({
        "status": "healthy",
        "project": PROJECT,
        "author": AUTHOR,
        "version": VERSION,
        "skills_count": manager.count(),
        "signature": "Mourad.Soltani"
    }), 200

@app.route("/")
def index():
    """Serve the main UI. Mourad.Soltani"""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/skills", methods=["GET"])
def list_skills():
    """List all skills. Mourad.Soltani"""
    category = request.args.get("category")
    q = request.args.get("q")
    skills = manager.list_skills(category=category, query=q)
    return jsonify({
        "skills": skills,
        "count": len(skills),
        "author": AUTHOR
    })

@app.route("/api/skills/<skill_id>", methods=["GET"])
def get_skill(skill_id):
    """Get single skill. Mourad.Soltani"""
    skill = manager.get_skill(skill_id)
    if not skill:
        return jsonify({"error": "Skill not found", "signature": AUTHOR}), 404
    return jsonify(skill)

@app.route("/api/skills", methods=["POST"])
def create_skill():
    """Create a new skill. Mourad.Soltani"""
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "name is required", "signature": AUTHOR}), 400
    skill = manager.create_skill(data)
    return jsonify(skill), 201

@app.route("/api/skills/<skill_id>", methods=["PUT"])
def update_skill(skill_id):
    """Update skill. Mourad.Soltani"""
    data = request.get_json() or {}
    skill = manager.update_skill(skill_id, data)
    if not skill:
        return jsonify({"error": "Skill not found", "signature": AUTHOR}), 404
    return jsonify(skill)

@app.route("/api/skills/<skill_id>", methods=["DELETE"])
def delete_skill(skill_id):
    """Delete skill. Mourad.Soltani"""
    ok = manager.delete_skill(skill_id)
    if not ok:
        return jsonify({"error": "Skill not found", "signature": AUTHOR}), 404
    return jsonify({"deleted": True, "signature": AUTHOR})

@app.route("/api/categories", methods=["GET"])
def categories():
    """List categories. Mourad.Soltani"""
    return jsonify({
        "categories": manager.categories(),
        "signature": AUTHOR
    })

@app.route("/api/export", methods=["GET"])
def export_pack():
    """Export all skills as a pack. Mourad.Soltani"""
    pack = manager.export_pack()
    return jsonify(pack)

@app.route("/api/stats", methods=["GET"])
def stats():
    """Project stats. Mourad.Soltani"""
    return jsonify({
        "project": PROJECT,
        "author": AUTHOR,
        "version": VERSION,
        "skills_count": manager.count(),
        "categories": manager.categories(),
        "signature": "Mourad.Soltani - Built with love for the 2026 AI Agent Skills wave"
    })

if __name__ == "__main__":
    print(f"Starting {PROJECT} by {AUTHOR} v{VERSION}")
    print("Signature: Mourad.Soltani")
    app.run(host="0.0.0.0", port=5000, debug=True)
