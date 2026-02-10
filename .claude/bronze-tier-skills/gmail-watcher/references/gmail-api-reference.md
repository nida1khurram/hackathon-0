# Gmail API Reference

## Useful Query Strings

| Query | Meaning |
|-------|---------|
| `is:unread is:important` | Unread + starred/important |
| `is:unread newer_than:1d` | Unread from last 24 hours |
| `is:unread label:inbox` | Unread in inbox only |
| `is:unread from:client@example.com` | Unread from specific sender |
| `subject:(invoice OR payment)` | Subject contains keywords |
| `has:attachment is:unread` | Unread with attachments |

## Common Label IDs

| Label | ID |
|-------|----|
| Inbox | `INBOX` |
| Important | `IMPORTANT` |
| Sent | `SENT` |
| Spam | `SPAM` |
| Starred | `STARRED` |
| Unread | `UNREAD` |

## API Rate Limits

- 250 quota units per user per second
- `messages.list` costs 5 units
- `messages.get` costs 5 units
- Daily limit: 1,000,000,000 units
- Safe polling: every 60–120 seconds at Bronze tier

## Scopes Required

Minimum scope for read-only monitoring:
```
https://www.googleapis.com/auth/gmail.readonly
```

For future send capability (Silver tier):
```
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.modify
```

## Message Object Key Fields

```python
msg['payload']['headers']   # From, To, Subject, Date
msg['snippet']              # First 200 chars of body
msg['labelIds']             # ['INBOX', 'UNREAD', 'IMPORTANT']
msg['id']                   # Unique message ID
msg['threadId']             # Thread grouping ID
```
