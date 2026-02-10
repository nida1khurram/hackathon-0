---
type: approval_request
action: {{ACTION_TYPE}}
source_file: {{SOURCE_FILE}}
created: {{TIMESTAMP}}
expires: {{EXPIRES}}
status: pending
priority: {{PRIORITY}}
---

# Approval Required: {{ACTION_TITLE}}

## What Needs Approval
{{ACTION_DESCRIPTION}}

## Details
| Field | Value |
|-------|-------|
| Action | {{ACTION_TYPE}} |
| Target | {{ACTION_TARGET}} |
| Amount | {{ACTION_AMOUNT}} |
| Reason | {{ACTION_REASON}} |

## Risk Assessment
{{RISK_NOTES}}

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.

## Expires
This request expires at **{{EXPIRES}}**.
If not actioned, it will be auto-archived to `/Done/` as `status: expired`.

---
*Created by AI Employee · Expires: {{EXPIRES}}*
