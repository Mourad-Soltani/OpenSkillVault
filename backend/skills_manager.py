# OpenSkillVault Skills Manager
# Author: Mourad.Soltani
# Signature: Mourad.Soltani

"""
Core skills management — Markdown + YAML frontmatter.
Optimized for local-first and serverless (/tmp) deployments.
"""

from __future__ import annotations

import os
import re
import shutil
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import yaml

from config import (
    AUTHOR,
    BUNDLED_SKILLS_DIR,
    MAX_CONTENT_LEN,
    MAX_DESC_LEN,
    MAX_NAME_LEN,
    MAX_TAGS,
    MAX_TITLE_LEN,
    SIGNATURE,
    SKILL_ID_RE,
    VERSION,
)

_ID_PATTERN = re.compile(SKILL_ID_RE)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(name: str) -> str:
    name = (name or "untitled").strip().lower()
    name = re.sub(r"[^a-z0-9\-_]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name[:MAX_NAME_LEN] or str(uuid.uuid4())[:8]


def _valid_id(skill_id: str) -> bool:
    return bool(skill_id and _ID_PATTERN.match(skill_id))


class SkillsManager:
    """Manages AI Agent Skills as Markdown files with YAML frontmatter. Mourad.Soltani"""

    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        os.makedirs(skills_dir, exist_ok=True)
        self._bootstrap()

    def _bootstrap(self) -> None:
        """Seed from bundled skills/ when vault is empty (works on Vercel /tmp)."""
        existing = [f for f in os.listdir(self.skills_dir) if f.endswith(".md")]
        if existing:
            return
        bundled = BUNDLED_SKILLS_DIR
        if os.path.isdir(bundled) and os.path.abspath(bundled) != os.path.abspath(
            self.skills_dir
        ):
            for fname in os.listdir(bundled):
                if fname.endswith(".md"):
                    src = os.path.join(bundled, fname)
                    dst = os.path.join(self.skills_dir, fname)
                    try:
                        shutil.copy2(src, dst)
                    except OSError:
                        pass
        # If still empty, write minimal seeds
        if not any(f.endswith(".md") for f in os.listdir(self.skills_dir)):
            for s in self._default_seeds():
                self.create_skill(s)

    @staticmethod
    def _default_seeds() -> List[Dict[str, Any]]:
        return [
            {
                "name": "code-reviewer",
                "title": "Code Reviewer Skill",
                "category": "engineering",
                "description": "Thorough code reviews: correctness, security, style.",
                "tags": ["code", "review", "security"],
                "content": (
                    "# Code Reviewer\n\nYou are an expert code reviewer.\n\n"
                    "## Checklist\n- Correctness\n- Security\n- Performance\n"
                    "- Readability\n- Tests\n\n## Output Format\n"
                    "Structured feedback with severity levels.\n\n"
                    "---\n*Skill by Mourad.Soltani*"
                ),
            },
            {
                "name": "taste-improver",
                "title": "Taste Improver",
                "category": "creative",
                "description": "Elevate AI output with craft and originality.",
                "tags": ["taste", "writing", "design"],
                "content": (
                    "# Taste Improver\n\nAvoid generic AI-slop. Prefer specificity "
                    "and craft.\n\n## Rules\n1. Reject clichés\n"
                    "2. Prefer concrete over abstract\n"
                    "3. Add one surprising but fitting detail\n\n"
                    "---\n*Signature: Mourad.Soltani*"
                ),
            },
            {
                "name": "research-synthesizer",
                "title": "Research Synthesizer",
                "category": "research",
                "description": "Synthesize multi-source research into actionable briefs.",
                "tags": ["research", "synthesis"],
                "content": (
                    "# Research Synthesizer\n\nCollect, rank, and synthesize sources.\n\n"
                    "## Process\n1. Extract claims\n2. Note confidence\n"
                    "3. Identify gaps\n4. Executive summary\n\n---\nMourad.Soltani"
                ),
            },
        ]

    def _skill_path(self, skill_id: str) -> Optional[str]:
        if not _valid_id(skill_id):
            return None
        path = os.path.join(self.skills_dir, f"{skill_id}.md")
        # Extra path-traversal guard
        if not os.path.abspath(path).startswith(os.path.abspath(self.skills_dir)):
            return None
        return path

    def _parse_frontmatter(self, text: str) -> tuple:
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1]) or {}
                    if not isinstance(meta, dict):
                        meta = {}
                    return meta, parts[2].strip()
                except Exception:
                    pass
        return {}, text

    def _to_markdown(self, meta: dict, body: str) -> str:
        meta = dict(meta)
        meta["author"] = AUTHOR
        meta["signature"] = SIGNATURE
        yaml_str = yaml.dump(meta, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return f"---\n{yaml_str}---\n\n{body}\n\n<!-- Mourad.Soltani -->\n"

    def _validate_payload(self, data: Dict, partial: bool = False) -> Optional[str]:
        if not partial and not data.get("name"):
            return "name is required"
        if "name" in data and data["name"] is not None:
            if len(str(data["name"])) > MAX_NAME_LEN:
                return f"name max {MAX_NAME_LEN} chars"
        if "title" in data and data["title"] is not None:
            if len(str(data["title"])) > MAX_TITLE_LEN:
                return f"title max {MAX_TITLE_LEN} chars"
        if "description" in data and data["description"] is not None:
            if len(str(data["description"])) > MAX_DESC_LEN:
                return f"description max {MAX_DESC_LEN} chars"
        if "content" in data and data["content"] is not None:
            if len(str(data["content"])) > MAX_CONTENT_LEN:
                return f"content max {MAX_CONTENT_LEN} chars"
        if "tags" in data and data["tags"] is not None:
            tags = data["tags"]
            if not isinstance(tags, list):
                return "tags must be a list"
            if len(tags) > MAX_TAGS:
                return f"max {MAX_TAGS} tags"
        return None

    def list_skills(
        self, category: Optional[str] = None, query: Optional[str] = None
    ) -> List[Dict]:
        results: List[Dict] = []
        try:
            names = sorted(os.listdir(self.skills_dir))
        except OSError:
            return results
        for fname in names:
            if not fname.endswith(".md"):
                continue
            skill_id = fname[:-3]
            skill = self.get_skill(skill_id)
            if not skill:
                continue
            if category and skill.get("category") != category:
                continue
            if query:
                q = query.lower().strip()
                blob = " ".join(
                    str(skill.get(k, ""))
                    for k in ("name", "title", "description", "content", "category")
                ).lower()
                tags = " ".join(skill.get("tags") or []).lower()
                if q not in blob and q not in tags:
                    continue
            # list view: omit full content for speed
            light = {k: v for k, v in skill.items() if k != "content"}
            light["content_preview"] = (skill.get("content") or "")[:160]
            results.append(light)
        return results

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        path = self._skill_path(skill_id)
        if not path or not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError:
            return None
        meta, body = self._parse_frontmatter(text)
        return {
            "id": skill_id,
            "name": meta.get("name", skill_id),
            "title": meta.get("title", skill_id),
            "category": meta.get("category", "general"),
            "description": meta.get("description", ""),
            "tags": meta.get("tags") or [],
            "created_at": meta.get("created_at"),
            "updated_at": meta.get("updated_at"),
            "author": meta.get("author", AUTHOR),
            "signature": SIGNATURE,
            "content": body,
        }

    def create_skill(self, data: Dict) -> Dict:
        err = self._validate_payload(data, partial=False)
        if err:
            raise ValueError(err)
        skill_id = _slugify(str(data.get("name", "untitled")))
        base = skill_id
        i = 1
        while self._skill_path(skill_id) and os.path.exists(self._skill_path(skill_id)):
            skill_id = f"{base}-{i}"[:MAX_NAME_LEN]
            i += 1
        now = _now()
        meta = {
            "name": skill_id,
            "title": str(data.get("title") or skill_id.replace("-", " ").title())[
                :MAX_TITLE_LEN
            ],
            "category": str(data.get("category") or "general")[:64],
            "description": str(data.get("description") or "")[:MAX_DESC_LEN],
            "tags": (data.get("tags") or [])[:MAX_TAGS],
            "created_at": now,
            "updated_at": now,
            "author": AUTHOR,
            "signature": SIGNATURE,
        }
        body = str(
            data.get("content")
            or f"# {meta['title']}\n\nSkill content here.\n\n---\n*Created by Mourad.Soltani*"
        )[:MAX_CONTENT_LEN]
        path = self._skill_path(skill_id)
        assert path
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._to_markdown(meta, body))
        return self.get_skill(skill_id)  # type: ignore

    def update_skill(self, skill_id: str, data: Dict) -> Optional[Dict]:
        if not _valid_id(skill_id):
            return None
        existing = self.get_skill(skill_id)
        if not existing:
            return None
        err = self._validate_payload(data, partial=True)
        if err:
            raise ValueError(err)
        meta = {
            "name": skill_id,
            "title": str(data.get("title", existing["title"]))[:MAX_TITLE_LEN],
            "category": str(data.get("category", existing["category"]))[:64],
            "description": str(data.get("description", existing["description"]))[
                :MAX_DESC_LEN
            ],
            "tags": (data.get("tags", existing.get("tags") or []))[:MAX_TAGS],
            "created_at": existing.get("created_at"),
            "updated_at": _now(),
            "author": AUTHOR,
            "signature": SIGNATURE,
        }
        body = str(data.get("content", existing["content"]))[:MAX_CONTENT_LEN]
        path = self._skill_path(skill_id)
        assert path
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._to_markdown(meta, body))
        return self.get_skill(skill_id)

    def delete_skill(self, skill_id: str) -> bool:
        path = self._skill_path(skill_id)
        if path and os.path.exists(path):
            os.remove(path)
            return True
        return False

    def count(self) -> int:
        try:
            return len([f for f in os.listdir(self.skills_dir) if f.endswith(".md")])
        except OSError:
            return 0

    def categories(self) -> List[str]:
        cats = set()
        for s in self.list_skills():
            cats.add(s.get("category") or "general")
        return sorted(cats)

    def export_pack(self) -> Dict:
        # Full content for export
        skills = []
        for light in self.list_skills():
            full = self.get_skill(light["id"])
            if full:
                skills.append(full)
        return {
            "name": "OpenSkillVault Pack",
            "author": AUTHOR,
            "signature": SIGNATURE,
            "version": VERSION,
            "exported_at": _now(),
            "skills_count": len(skills),
            "skills": skills,
        }

    def import_pack(self, pack: Dict, overwrite: bool = False) -> Dict:
        """Import skills from an export pack. Returns counts."""
        skills = pack.get("skills") or []
        created = updated = skipped = 0
        for item in skills:
            if not isinstance(item, dict):
                skipped += 1
                continue
            name = item.get("name") or item.get("id")
            if not name:
                skipped += 1
                continue
            skill_id = _slugify(str(name))
            exists = self.get_skill(skill_id) is not None
            payload = {
                "name": skill_id,
                "title": item.get("title"),
                "category": item.get("category"),
                "description": item.get("description"),
                "tags": item.get("tags") or [],
                "content": item.get("content") or "",
            }
            try:
                if exists and overwrite:
                    self.update_skill(skill_id, payload)
                    updated += 1
                elif exists:
                    skipped += 1
                else:
                    self.create_skill(payload)
                    created += 1
            except ValueError:
                skipped += 1
        return {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "signature": SIGNATURE,
        }
