#!/usr/bin/env python3
"""
validate_handbook.py — Validate Company_Handbook.md for completeness.

Usage:
    python validate_handbook.py
    python validate_handbook.py --fix   # Auto-add missing sections with defaults

Environment variables (.env):
    VAULT_PATH   Path to Obsidian vault root
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("handbook-validator")

VAULT_PATH = Path(os.getenv("VAULT_PATH", "~/AI_Employee_Vault")).expanduser()

REQUIRED_SECTIONS = [
    ("## 1. Identity", "Owner name, business name, AI employee name"),
    ("## 2. Communication Rules", "Email and WhatsApp behavior guidelines"),
    ("## 3. Financial Rules", "Payment thresholds and approval requirements"),
    ("## 4. Autonomy Thresholds", "Table of auto-approve vs. requires-approval actions"),
    ("## 5. Priority Keywords", "List of keywords that trigger high-priority routing"),
    ("## 6. Business Hours", "Operating hours and after-hours behavior"),
    ("## 7. Privacy Rules", "Data handling and confidentiality rules"),
    ("## 8. Escalation Path", "What to do when uncertain or an error occurs"),
]

DEFAULT_ADDITIONS = {
    "## 6. Business Hours": """## 6. Business Hours

- Working hours: 9:00 AM – 6:00 PM (your timezone)
- Outside hours: collect and queue items, do NOT send responses
- Emergency override: messages tagged #emergency are processed 24/7
""",
    "## 7. Privacy Rules": """## 7. Privacy Rules

- Never log personal/sensitive conversation content verbatim
- Summarize message content in action files — do not copy full text
- Never store banking credentials in the vault
- All external API keys live in `.env` (never in vault)
""",
    "## 8. Escalation Path": """## 8. Escalation Path

When uncertain → create a `PLAN_*.md` with `status: needs_human_review`
When dangerous action needed → create `APPROVAL_*.md` in `/Pending_Approval`
When system error → write to `/Logs/errors.md`
""",
}


def validate(handbook_path: Path, fix: bool = False) -> bool:
    if not handbook_path.exists():
        logger.error(f"Company_Handbook.md not found at {handbook_path}")
        logger.error("Run the company-handbook skill to create it.")
        return False

    content = handbook_path.read_text(encoding="utf-8")
    missing = []

    print(f"\n📖 Validating: {handbook_path}\n")
    for section_header, description in REQUIRED_SECTIONS:
        present = section_header.lower() in content.lower()
        status = "✅" if present else "❌"
        print(f"  {status} {section_header} — {description}")
        if not present:
            missing.append(section_header)

    if not missing:
        print("\n✅ Handbook is complete! All required sections found.\n")
        return True

    print(f"\n⚠️  Missing {len(missing)} section(s): {', '.join(missing)}\n")

    if fix:
        print("Auto-adding missing sections with safe defaults...\n")
        for section in missing:
            if section in DEFAULT_ADDITIONS:
                content += "\n---\n" + DEFAULT_ADDITIONS[section]
                print(f"  ➕ Added: {section}")
            else:
                placeholder = f"\n---\n{section}\n\n*(Please fill in this section)*\n"
                content += placeholder
                print(f"  ➕ Added placeholder: {section}")
        handbook_path.write_text(content, encoding="utf-8")
        print("\n✅ Handbook updated. Please review and customize the added sections.\n")
        return True

    print("Run with --fix to auto-add missing sections with safe defaults.\n")
    return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate Company_Handbook.md")
    parser.add_argument("--fix", action="store_true", help="Auto-add missing sections")
    args = parser.parse_args()

    handbook_path = VAULT_PATH / "Company_Handbook.md"
    success = validate(handbook_path, fix=args.fix)
    sys.exit(0 if success else 1)
