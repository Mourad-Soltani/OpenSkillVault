# OpenSkillVault Skills Manager
# Author: Mourad.Soltani
# Signature: Mourad.Soltani everywhere

"""
Core skills management logic.
Inspired by trending 2026 agent skills projects (mattpocock/skills, taste-skill, etc.).
"""

import os
import json
import uuid
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import yaml

AUTHOR = "Mourad.Soltani"

class SkillsManager:
    """Manages AI Agent Skills as Markdown files with YAML frontmatter. Mourad.Soltani"""

    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        os.makedirs(skills_dir, exist_ok=True)
        self._ensure_seed()

    def _ensure_seed(self):
        """Seed with example skills if empty. Mourad.Soltani"""
        if not any(f.endswith(".md") for f in os.listdir(self.skills_dir)):
            seeds = [
                {
                    "name": "code-reviewer",
                    "title": "Code Reviewer Skill",
                    "category": "engineering",
                    "description": "Perform thorough code reviews focusing on correctness, security, and style.",
                    "content": "# Code Reviewer\n\nYou are an expert code reviewer.\n\n## Checklist\n- Correctness\n- Security\n- Performance\n- Readability\n- Tests\n\n## Output Format\nProvide structured feedback with severity levels.\n\n---\n*Skill by Mourad.Soltani*"
                },
                {
                    "name": "taste-improver",
                    "title": "Taste Improver (inspired by taste-skill)",
                    "category": "creative",
                    "description": "Elevate AI-generated content with better aesthetic judgment and originality.",
                    "content": "# Taste Improver\n\nAvoid generic AI-slop. Prefer specificity, craft, and unexpected but coherent choices.\n\n## Rules\n1. Reject clichés\n2. Prefer concrete over abstract\n3. Add one surprising but fitting detail\n\n---\n*Signature: Mourad.Soltani*"
                },
                {
                    "name": "research-synthesizer",
                    "title": "Research Synthesizer",
                    "category": "research",
                    "description": "Synthesize multi-source research into clear, actionable briefs.",
                    "content": "# Research Synthesizer\n\nCollect, rank, and synthesize sources.\n\n## Process\n1. Extract claims\n2. Note confidence\n3. Identify gaps\n4. Produce executive summary\n\n---\nMourad.Soltani"
                }
            ]
            for s in seeds:
                self.create_skill(s)

    def _skill_path(self, skill_id: str) -> str:
        return os.path.join(self.skills_dir, f"{skill_id}.md")

    def _parse_frontmatter(self, text: str) -> tuple:
        """Parse YAML frontmatter. Mourad.Soltani"""
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1]) or {}
                    body = parts[2].strip()
                    return meta, body
                except Exception:
                    pass
        return {}, text

    def _to_markdown(self, meta: dict, body: str) -> str:
        """Serialize to Markdown with frontmatter. Mourad.Soltani"""
        meta = dict(meta)
        meta["author"] = AUTHOR
        meta["signature"] = "Mourad.Soltani"
        yaml_str = yaml.dump(meta, default_flow_style=False, allow_unicode=True)
        return f"---\n{yaml_str}---\n\n{body}\n\n<!-- Mourad.Soltani -->\n"

    def list_skills(self, category: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
        """List skills with optional filters. Mourad.Soltani"""
        results = []
        for fname in sorted(os.listdir(self.skills_dir)):
            if not fname.endswith(".md"):
                continue
            skill_id = fname[:-3]
            skill = self.get_skill(skill_id)
            if not skill:
                continue
            if category and skill.get("category") != category:
                continue
            if query:
                q = query.lower()
                searchable = f"{skill.get('name','')} {skill.get('title','')} {skill.get('description','')} {skill.get('content','')}".lower()
                if q not in searchable:
                    continue
            results.append(skill)
        return results

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """Load one skill. Mourad.Soltani"""
        path = self._skill_path(skill_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        meta, body = self._parse_frontmatter(text)
        return {
            "id": skill_id,
            "name": meta.get("name", skill_id),
            "title": meta.get("title", skill_id),
            "category": meta.get("category", "general"),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "created_at": meta.get("created_at"),
            "updated_at": meta.get("updated_at"),
            "author": meta.get("author", AUTHOR),
            "signature": "Mourad.Soltani",
            "content": body
        }

    def create_skill(self, data: Dict) -> Dict:
        """Create new skill. Mourad.Soltani"""
        name = data.get("name", "untitled").strip().lower()
        name = re.sub(r"[^a-z0-9\-_]", "-", name)
        skill_id = name or str(uuid.uuid4())[:8]
        # ensure unique
        base = skill_id
        i = 1
        while os.path.exists(self._skill_path(skill_id)):
            skill_id = f"{base}-{i}"
            i += 1

        now = datetime.now(timezone.utc).isoformat()
        meta = {
            "name": skill_id,
            "title": data.get("title", skill_id.replace("-", " ").title()),
            "category": data.get("category", "general"),
            "description": data.get("description", ""),
            "tags": data.get("tags", []),
            "created_at": now,
            "updated_at": now,
            "author": AUTHOR,
            "signature": "Mourad.Soltani"
        }
        body = data.get("content", f"# {meta['title']}\n\nSkill content here.\n\n---\n*Created by Mourad.Soltani*")
        md = self._to_markdown(meta, body)
        with open(self._skill_path(skill_id), "w", encoding="utf-8") as f:
            f.write(md)
        return self.get_skill(skill_id)

    def update_skill(self, skill_id: str, data: Dict) -> Optional[Dict]:
        """Update existing skill. Mourad.Soltani"""
        existing = self.get_skill(skill_id)
        if not existing:
            return None
        now = datetime.now(timezone.utc).isoformat()
        meta = {
            "name": skill_id,
            "title": data.get("title", existing["title"]),
            "category": data.get("category", existing["category"]),
            "description": data.get("description", existing["description"]),
            "tags": data.get("tags", existing.get("tags", [])),
            "created_at": existing.get("created_at"),
            "updated_at": now,
            "author": AUTHOR,
            "signature": "Mourad.Soltani"
        }
        body = data.get("content", existing["content"])
        md = self._to_markdown(meta, body)
        with open(self._skill_path(skill_id), "w", encoding="utf-8") as f:
            f.write(md)
        return self.get_skill(skill_id)

    def delete_skill(self, skill_id: str) -> bool:
        """Delete skill. Mourad.Soltani"""
        path = self._skill_path(skill_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def count(self) -> int:
        return len([f for f in os.listdir(self.skills_dir) if f.endswith(".md")])

    def categories(self) -> List[str]:
        cats = set()
        for s in self.list_skills():
            cats.add(s.get("category", "general"))
        return sorted(list(cats))

    def export_pack(self) -> Dict:
        """Export full skill pack. Mourad.Soltani"""
        skills = self.list_skills()
        return {
            "name": "OpenSkillVault Pack",
            "author": AUTHOR,
            "signature": "Mourad.Soltani",
            "version": "1.0.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "skills_count": len(skills),
            "skills": skills
        }
