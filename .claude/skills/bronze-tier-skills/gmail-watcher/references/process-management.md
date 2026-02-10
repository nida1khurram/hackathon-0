# Process Management for Watchers

Watcher scripts are daemon processes that must survive crashes and reboots.
Never run them with a bare `python script.py` in production.

## Option 1: PM2 (Recommended for Hackathon)

PM2 is a Node.js process manager that handles Python perfectly.

```bash
# Install
npm install -g pm2

# Start watcher
pm2 start scripts/gmail_watcher.py --interpreter python3 --name gmail-watcher

# Check status
pm2 status

# View logs
pm2 logs gmail-watcher

# Restart
pm2 restart gmail-watcher

# Save process list (survives reboots)
pm2 save
pm2 startup   # follow printed instructions
```

## Option 2: supervisord (Linux/Mac)

```ini
# /etc/supervisor/conf.d/gmail_watcher.conf
[program:gmail_watcher]
command=python3 /path/to/scripts/gmail_watcher.py
directory=/path/to/project
autostart=true
autorestart=true
stderr_logfile=/var/log/gmail_watcher.err.log
stdout_logfile=/var/log/gmail_watcher.out.log
environment=VAULT_PATH="/path/to/vault"
```

```bash
supervisorctl reread && supervisorctl update && supervisorctl start gmail_watcher
```

## Option 3: systemd (Linux)

```ini
# /etc/systemd/system/gmail-watcher.service
[Unit]
Description=AI Employee Gmail Watcher
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/project
EnvironmentFile=/path/to/.env
ExecStart=/usr/bin/python3 scripts/gmail_watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable gmail-watcher && systemctl start gmail-watcher
```

## Option 4: Built-in Python Watchdog (Bronze Tier Quick Start)

Use `scripts/watchdog.py` from the hackathon project to auto-restart crashed processes.
See the project's Watchdog pattern for implementation details.

## Choosing the Right Option

| Situation | Recommendation |
|-----------|---------------|
| Hackathon / development | PM2 |
| Linux server | systemd |
| Multi-process management | supervisord |
| Quick local test | Direct `python` |
