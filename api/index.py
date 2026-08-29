# OpenSkillVault — Vercel Python entrypoint
# Author: Mourad.Soltani
# Signature: Mourad.Soltani

"""
Vercel serverless entry for Flask app.
On Vercel the filesystem is read-only except /tmp — skills are stored under /tmp when VERCEL=1.
"""

import os
import sys

# Ensure project root and backend are importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
sys.path.insert(0, ROOT)
sys.path.insert(0, BACKEND)

# Writable skills dir on serverless
if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    skills_dir = os.path.join("/tmp", "openskillvault-skills")
    os.makedirs(skills_dir, exist_ok=True)
    os.environ["OPENSKILLVAULT_SKILLS_DIR"] = skills_dir

from backend.app import app  # noqa: E402

# Vercel Python looks for `app` (WSGI)
# Signature: Mourad.Soltani
