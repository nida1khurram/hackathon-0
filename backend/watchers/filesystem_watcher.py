"""
filesystem_watcher.py — Watch vault/Inbox/ for new files and create action items.

Runs as a background async task inside FastAPI's lifespan.
When a new file lands in Inbox/, creates a corresponding FILE_<name>.md in Needs_Action/.
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

logger = logging.getLogger("fs-watcher")


class InboxHandler(FileSystemEventHandler):
    """React to new files created in the Inbox folder."""

    def __init__(self, vault_path: Path, dry_run: bool = True):
        super().__init__()
        self.vault_path = vault_path
        self.dry_run = dry_run

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return

        src = Path(event.src_path)
        self._process_file(src)

    def _process_file(self, filepath: Path):
        needs_action = self.vault_path / "Needs_Action"
        needs_action.mkdir(parents=True, exist_ok=True)

        safe_name = filepath.stem.replace(" ", "_")
        action_file = needs_action / f"FILE_{safe_name}.md"

        if action_file.exists():
            logger.debug("Action file already exists: %s", action_file.name)
            return

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        content = f"""---
type: file_intake
source: inbox
original_name: {filepath.name}
received: {timestamp}
priority: medium
status: pending
---

## File Received
- **Name**: {filepath.name}
- **Size**: {filepath.stat().st_size} bytes
- **Received**: {timestamp}

## Suggested Actions
- [ ] Review file contents
- [ ] Route to appropriate folder
- [ ] Archive or delete after processing
"""

        if self.dry_run:
            logger.info(
                "[DRY RUN] Would create: %s for inbox file: %s",
                action_file.name, filepath.name,
            )
        else:
            action_file.write_text(content, encoding="utf-8")
            logger.info("Created: %s (source=%s)", action_file.name, filepath.name)


async def run_filesystem_watcher_async(vault_path: Path, dry_run: bool = True):
    """Long-running async task that watches vault/Inbox/ for new files."""
    inbox = vault_path / "Inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    logger.info("[FS] Starting | watching=%s | dry_run=%s", inbox, dry_run)

    handler = InboxHandler(vault_path, dry_run=dry_run)
    observer = Observer()
    observer.schedule(handler, str(inbox), recursive=False)
    observer.start()

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("[FS] Watcher stopping...")
    finally:
        observer.stop()
        observer.join()
        logger.info("[FS] Watcher stopped")
