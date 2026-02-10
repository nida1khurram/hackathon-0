# Autonomy Guide

## The Autonomy Spectrum

```
FULLY MANUAL ←──────────────────────────────→ FULLY AUTONOMOUS
    |                                                |
Human does                                  AI does everything
everything                                  no human needed

Bronze Tier: ~30% autonomous
Silver Tier: ~60% autonomous
Gold Tier:   ~80% autonomous (payments always manual)
```

## Bronze Tier Recommended Defaults

At Bronze tier, err on the side of caution. Start conservative and loosen over time.

### Always Auto-Approve (Safe)
- Reading and logging any data
- Creating plan and note files in the vault
- Updating Dashboard.md
- Moving files between folders within the vault

### Always Require Approval (Never Auto)
- Sending any email or message
- Any financial transaction
- Deleting any file
- Accessing new external services or APIs
- Actions that cannot be easily undone

### Configurable (Choose Based on Trust Level)
- Drafting replies (auto-draft vs. require approval for drafts)
- Social media scheduling (draft only vs. draft + queue)
- Internal file organization (auto vs. manual)

## Common Mistakes to Avoid

| Mistake | Risk | Fix |
|---------|------|-----|
| Setting send_email to auto-approve | AI sends emails you didn't review | Always require approval for sends |
| No payment threshold | AI could initiate any payment | Set threshold at $50-$100 |
| Vague keywords like "important" | Too many false positives or misses | Use specific business terms |
| No escalation path | Errors go unnoticed | Define a log file + alert method |

## Tuning Your Autonomy Over Time

After 1 week: Review the `/Done` folder. Were any auto-approved items wrong?
After 2 weeks: Look at `/Pending_Approval`. Are there items that could be auto-approved?
Monthly: Adjust thresholds based on real performance.

**Golden rule**: If the AI has made 0 mistakes on a category for 30 days, consider automating it further.
