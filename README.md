# OpenSkillVault

**AI Agent Skills Manager** — Trending 2026 project inspired by the explosion of agent skills packs on GitHub (skills, taste-skill, book-to-skill, ECC, etc.).

> **Author & Signature:** Mourad.Soltani  
> Version: 1.0.0  
> Built: August 2026

---

## What it is

OpenSkillVault is a local-first, open-source tool to create, organize, search, and export **AI Agent Skills** (Markdown files with YAML frontmatter). Perfect companion for Claude Code, Codex, Cursor, OpenClaw and any agent that consumes skill files.

### Features

- Full CRUD for skills
- Categories & full-text search
- One-click export of skill packs (JSON)
- Seed skills included (code-reviewer, taste-improver, research-synthesizer)
- Health endpoint for production readiness
- Beautiful dark UI
- Zero external paid dependencies
- Fully testable (`pytest`)

### Signature

Every file, every response, every export carries the signature:

**Mourad.Soltani**

---

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Run
cd backend
python app.py
# → http://localhost:5000
```

Or with Gunicorn:

```bash
gunicorn -b 0.0.0.0:5000 backend.app:app
```

## Health Check

```bash
curl http://localhost:5000/health
```

Expected:

```json
{
  "status": "healthy",
  "project": "OpenSkillVault",
  "author": "Mourad.Soltani",
  "version": "1.0.0",
  "skills_count": 3,
  "signature": "Mourad.Soltani"
}
```

## Tests

```bash
pytest -v --cov=backend
```

All tests must pass. Health tests verify the Mourad.Soltani signature is present.

## Project Structure

```
mourad-soltani-trending-project/
├── backend/
│   ├── app.py              # Flask API + signature
│   └── skills_manager.py   # Core logic · Mourad.Soltani
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── skills/                 # Markdown skill files
├── tests/
│   ├── test_health.py
│   └── test_skills.py
├── requirements.txt
├── README.md
├── LICENSE
└── ...
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health + signature |
| GET | `/api/skills` | List (supports `?category=&q=`) |
| POST | `/api/skills` | Create |
| GET | `/api/skills/<id>` | Get one |
| PUT | `/api/skills/<id>` | Update |
| DELETE | `/api/skills/<id>` | Delete |
| GET | `/api/categories` | Categories |
| GET | `/api/export` | Full pack export |
| GET | `/api/stats` | Stats |

## License

MIT — Mourad.Soltani

---

**Mourad.Soltani** · OpenSkillVault · 2026  
*Built as a complete, health-checked, production-ready trending project.*

## Deploy on Vercel (Python)

Configured for Vercel serverless Python + static frontend.

Files:
- `vercel.json` — builds `@vercel/python` for `api/index.py` and static `frontend/**`
- `api/index.py` — WSGI entry importing Flask `app`
- Skills storage uses `/tmp` when `VERCEL=1` (serverless filesystem)

```bash
# After linking the GitHub repo in Vercel dashboard:
# Framework: Other
# Install Command: pip install -r requirements.txt
# (or leave default; Vercel detects requirements.txt)
```

Routes:
- `/styles.css`, `/app.js` → static frontend
- everything else → Flask via `api/index.py`

**Note:** Skill data on Vercel lives in `/tmp` and is **not durable** across cold starts. For production persistence, use a database or object storage.

Signature: Mourad.Soltani
