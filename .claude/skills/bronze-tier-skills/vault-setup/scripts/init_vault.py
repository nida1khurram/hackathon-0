#!/usr/bin/env python3
"""
init_vault.py — Scaffold an AI Employee Obsidian vault.

Usage:
    python init_vault.py --vault ~/AI_Employee_Vault --owner "Jane Doe" --business "Acme Co"
    python init_vault.py --vault ~/AI_Employee_Vault --owner "Jane Doe" --business "Acme Co" --dry-run
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


FOLDERS = [
    "Inbox",
    "Needs_Action",
    "In_Progress",
    "Plans",
    "Pending_Approval",
    "Approved",
    "Rejected",
    "Done",
    "Logs",
    "Briefings",
    "Accounting",
]

CORE_FILES = {
    "Dashboard.md": "assets/dashboard-template.md",
    "Company_Handbook.md": "assets/handbook-template.md",
    "Business_Goals.md": "assets/goals-template.md",
    ".gitignore": "assets/gitignore-template.txt",
}


def resolve_templates_dir() -> Path:
    """Find the assets/ directory relative to this script."""
    return Path(__file__).parent.parent / "assets"


def render_template(template_path: Path, owner: str, business: str) -> str:
    """Substitute placeholder tokens in a template file."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("{{OWNER}}", owner)
    content = content.replace("{{BUSINESS}}", business)
    content = content.replace("{{TIMESTAMP}}", timestamp)
    return content


def scaffold_vault(vault_path: Path, owner: str, business: str, dry_run: bool = False) -> None:
    templates_dir = resolve_templates_dir()

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Scaffolding vault at: {vault_path}\n")

    # 1. Create folders
    for folder in FOLDERS:
        target = vault_path / folder
        print(f"  📁 {'Would create' if dry_run else 'Creating'}: {target}")
        if not dry_run:
            target.mkdir(parents=True, exist_ok=True)

    # 2. Write core files
    print()
    for filename, template_rel in CORE_FILES.items():
        dest = vault_path / filename
        template_path = templates_dir / Path(template_rel).name

        if dest.exists() and not dry_run:
            answer = input(f"  ⚠️  {filename} already exists. Overwrite? [y/N]: ").strip().lower()
            if answer != "y":
                print(f"  ⏭️  Skipped: {filename}")
                continue

        if not template_path.exists():
            print(f"  ❌ Template not found: {template_path} — skipping {filename}")
            continue

        content = render_template(template_path, owner, business)
        print(f"  📄 {'Would write' if dry_run else 'Writing'}: {dest}")
        if not dry_run:
            dest.write_text(content, encoding="utf-8")

    # 3. Print summary
    print(f"\n{'[DRY RUN] ' if dry_run else ''}✅ Vault scaffold complete!\n")
    if not dry_run:
        print("Next steps:")
        print("  1. Open the vault in Obsidian")
        print("  2. Fill in Company_Handbook.md with your rules")
        print("  3. Set your revenue targets in Business_Goals.md")
        print("  4. Run the gmail-watcher or file-processor skill\n")


def main():
    parser = argparse.ArgumentParser(description="Initialize an AI Employee Obsidian vault")
    parser.add_argument("--vault", required=True, help="Path to vault root directory")
    parser.add_argument("--owner", required=True, help="Your name (e.g. 'Jane Doe')")
    parser.add_argument("--business", required=True, help="Business name (e.g. 'Acme Co')")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    args = parser.parse_args()

    vault_path = Path(args.vault).expanduser().resolve()
    scaffold_vault(vault_path, args.owner, args.business, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
