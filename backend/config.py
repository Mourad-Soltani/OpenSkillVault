# OpenSkillVault config — Mourad.Soltani
"""Central configuration. Signature: Mourad.Soltani"""

import os

AUTHOR = "Mourad.Soltani"
PROJECT = "OpenSkillVault"
VERSION = "1.1.0"
SIGNATURE = "Mourad.Soltani"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Serverless-friendly skills path
SKILLS_DIR = os.environ.get(
    "OPENSKILLVAULT_SKILLS_DIR",
    os.path.join(BASE_DIR, "skills"),
)
DATA_DIR = os.path.join(BASE_DIR, "data")
# Bundled seed skills shipped with the repo (read-only on Vercel)
BUNDLED_SKILLS_DIR = os.path.join(BASE_DIR, "skills")

# Security: skill ids must match this pattern (no path traversal)
SKILL_ID_RE = r"^[a-z0-9][a-z0-9\-_]{0,63}$"

MAX_NAME_LEN = 64
MAX_TITLE_LEN = 120
MAX_DESC_LEN = 500
MAX_CONTENT_LEN = 100_000
MAX_TAGS = 20
