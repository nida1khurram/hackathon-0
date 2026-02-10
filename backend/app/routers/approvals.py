import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models.approval import Approval
from app.services.file_processor import _parse_frontmatter, _get_body

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


def _read_approvals() -> list[Approval]:
    """Read all approval files from Pending_Approval folder."""
    approval_dir = settings.vault_dir / "Pending_Approval"
    if not approval_dir.exists():
        return []

    approvals: list[Approval] = []
    for filepath in sorted(approval_dir.glob("*.md")):
        text = filepath.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)

        approval = Approval(
            id=meta.get("id", filepath.stem),
            filename=filepath.name,
            action=meta.get("action", "review_and_respond"),
            source_file=meta.get("source_file", ""),
            created=meta.get("created", ""),
            expires=meta.get("expires", "24h"),
            status=meta.get("status", "pending"),
            priority=meta.get("priority", "normal"),
            subject=meta.get("subject", filepath.stem),
            reason=meta.get("reason", ""),
        )
        approvals.append(approval)

    return approvals


def _move_approval(approval_id: str, destination: str) -> str:
    """Move an approval file to Approved or Rejected folder."""
    approval_dir = settings.vault_dir / "Pending_Approval"
    dest_dir = settings.vault_dir / destination
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Find the file by id
    target_file: Path | None = None
    if approval_dir.exists():
        for filepath in approval_dir.glob("*.md"):
            text = filepath.read_text(encoding="utf-8")
            meta = _parse_frontmatter(text)
            if meta.get("id") == approval_id:
                target_file = filepath
                break

    if target_file is None:
        # Try matching by filename pattern
        pattern_file = approval_dir / f"APPROVAL_{approval_id}.md"
        if pattern_file.exists():
            target_file = pattern_file

    if target_file is None:
        raise HTTPException(status_code=404, detail=f"Approval {approval_id} not found")

    # Also move the source file from In_Progress to Done (if approving) or back to Needs_Action (if rejecting)
    text = target_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(text)
    source_filename = meta.get("source_file", "")

    # Move approval file
    shutil.move(str(target_file), str(dest_dir / target_file.name))

    # Move source file if it exists in In_Progress
    if source_filename:
        in_progress_dir = settings.vault_dir / "In_Progress"
        source_path = in_progress_dir / source_filename
        if source_path.exists():
            if destination == "Approved":
                done_dir = settings.vault_dir / "Done"
                done_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(done_dir / source_filename))
            elif destination == "Rejected":
                needs_action_dir = settings.vault_dir / "Needs_Action"
                needs_action_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(needs_action_dir / source_filename))

    return target_file.name


@router.get("", response_model=list[Approval])
def list_approvals():
    """List all pending approval requests."""
    return _read_approvals()


@router.post("/{approval_id}/approve")
def approve_item(approval_id: str):
    """Approve a pending item - moves it to Approved folder."""
    filename = _move_approval(approval_id, "Approved")
    return {"message": f"Approved: {filename}. Source file moved to Done."}


@router.post("/{approval_id}/reject")
def reject_item(approval_id: str):
    """Reject a pending item - moves it to Rejected folder."""
    filename = _move_approval(approval_id, "Rejected")
    return {"message": f"Rejected: {filename}. Source file returned to Needs_Action."}
