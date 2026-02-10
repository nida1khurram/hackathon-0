import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import vault, needs_action, approvals, dashboard, handbook, simulate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background watchers on startup, cancel on shutdown."""
    tasks: list[asyncio.Task] = []

    # Filesystem watcher — always starts
    from watchers.filesystem_watcher import run_filesystem_watcher_async
    fs_task = asyncio.create_task(
        run_filesystem_watcher_async(settings.vault_dir, dry_run=settings.DRY_RUN)
    )
    tasks.append(fs_task)
    logger.info("Filesystem watcher started (vault/Inbox/)")

    # Gmail watcher — only if credentials exist
    if settings.credentials_path.exists():
        from watchers.gmail_watcher import run_gmail_watcher_async
        gmail_task = asyncio.create_task(
            run_gmail_watcher_async(
                vault_path=settings.vault_dir,
                credentials_path=settings.credentials_path,
                token_path=settings.token_path,
                poll_interval=settings.GMAIL_POLL_INTERVAL,
                query=settings.GMAIL_QUERY,
                dry_run=settings.DRY_RUN,
            )
        )
        tasks.append(gmail_task)
        logger.info("Gmail watcher started")
    else:
        logger.warning(
            "Gmail watcher NOT started — credentials.json not found at %s. "
            "See README for OAuth setup instructions.",
            settings.credentials_path,
        )

    yield

    # Shutdown: cancel all background tasks
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Background watchers stopped")


app = FastAPI(title="AI Employee Dashboard API", lifespan=lifespan)

# Parse CORS origins from settings (JSON string -> list)
try:
    origins = json.loads(settings.CORS_ORIGINS)
except (json.JSONDecodeError, TypeError):
    origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vault.router)
app.include_router(needs_action.router)
app.include_router(approvals.router)
app.include_router(dashboard.router)
app.include_router(handbook.router)
app.include_router(simulate.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
