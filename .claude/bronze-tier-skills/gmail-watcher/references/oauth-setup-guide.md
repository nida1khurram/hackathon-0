# Gmail OAuth Setup Guide

## Step-by-Step

### 1. Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Create a new project (e.g., "AI Employee")
3. Enable the **Gmail API**: APIs & Services → Library → search "Gmail" → Enable

### 2. Create OAuth 2.0 Credentials

1. APIs & Services → Credentials → Create Credentials → OAuth client ID
2. Application type: **Desktop app**
3. Name: "AI Employee Local"
4. Click Create → Download JSON
5. Rename to `credentials.json`
6. Place in your project root (NOT inside the Obsidian vault)

### 3. Configure OAuth Consent Screen

1. APIs & Services → OAuth consent screen
2. User type: **External** (for personal use)
3. Add your Gmail as a test user
4. Scopes: add `gmail.readonly`
5. Save

### 4. First-Time Token Generation

Run the setup command:
```bash
python scripts/gmail_watcher.py --setup
```

This will:
- Open a browser at `localhost:8080`
- Ask you to sign in and grant access
- Save `token.json` to the path in your `.env`

### 5. Token Refresh

`google-auth` refreshes tokens automatically.
If refresh fails (e.g., revoked access), the watcher logs an error and exits.
Re-run `--setup` to re-authorize.

## Security Checklist

- [ ] `credentials.json` is in `.gitignore`
- [ ] `token.json` is in `.gitignore`
- [ ] Neither file is inside the Obsidian vault
- [ ] OAuth consent screen has only required scopes
- [ ] Only your email is in the test users list
