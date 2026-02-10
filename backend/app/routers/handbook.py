from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models.handbook import HandbookData, HandbookUpdate, SectionValidation

router = APIRouter(prefix="/api/handbook", tags=["handbook"])

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


def _validate_content(content: str) -> tuple[list[SectionValidation], bool]:
    """Validate handbook content against required sections."""
    validations: list[SectionValidation] = []
    all_present = True

    for section_header, description in REQUIRED_SECTIONS:
        present = section_header in content
        if not present:
            all_present = False
        validations.append(
            SectionValidation(
                section=section_header,
                description=description,
                present=present,
            )
        )

    return validations, all_present


def _read_handbook() -> str:
    """Read the Company_Handbook.md file from the vault."""
    handbook_path = settings.vault_dir / "Company_Handbook.md"
    if not handbook_path.exists():
        return ""
    return handbook_path.read_text(encoding="utf-8")


@router.get("", response_model=HandbookData)
def get_handbook():
    """Get the handbook content with validation status."""
    content = _read_handbook()
    if not content:
        raise HTTPException(status_code=404, detail="Company_Handbook.md not found. Initialize the vault first.")

    validations, is_complete = _validate_content(content)
    return HandbookData(
        content=content,
        validation=validations,
        is_complete=is_complete,
    )


@router.put("")
def update_handbook(update: HandbookUpdate):
    """Update the Company_Handbook.md file."""
    handbook_path = settings.vault_dir / "Company_Handbook.md"
    if not handbook_path.parent.exists():
        raise HTTPException(status_code=404, detail="Vault not initialized. Run vault init first.")

    handbook_path.write_text(update.content, encoding="utf-8")
    return {"message": "Handbook updated successfully."}


@router.post("/validate", response_model=HandbookData)
def validate_handbook():
    """Validate the current handbook against required sections."""
    content = _read_handbook()
    if not content:
        raise HTTPException(status_code=404, detail="Company_Handbook.md not found. Initialize the vault first.")

    validations, is_complete = _validate_content(content)
    return HandbookData(
        content=content,
        validation=validations,
        is_complete=is_complete,
    )
