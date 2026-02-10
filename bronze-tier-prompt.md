# Claude Code Prompt — HAC0 Bronze Tier
# Personal AI Employee — Full Stack (Next.js + FastAPI)
# Paste this entire prompt into Claude Code to begin.

---

You are building the **HAC0 Bronze Tier Personal AI Employee** — a fully functional
Digital FTE (Full-Time Equivalent) system. Work autonomously, use all available tools,
read every referenced SKILL.md before touching code, and do not stop until every
deliverable is complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 0 — SKILLS & MCP SETUP (DO THIS FIRST)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before writing a single line of code, read all 5 Bronze Tier skills in this order:

1. Read `.claude/skills/vault-setup/SKILL.md`
2. Read `.claude/skills/gmail-watcher/SKILL.md`
3. Read `.claude/skills/file-processor/SKILL.md`
4. Read `.claude/skills/dashboard-updater/SKILL.md`
5. Read `.claude/skills/company-handbook/SKILL.md`

Then configure the Context7 MCP server by adding this to `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {}
    }
  }
}
```

Use Context7 throughout development to resolve library docs for:
Next.js 15, FastAPI, Pydantic v2, SQLModel, python-dotenv, google-auth,
watchdog, Tailwind CSS v4, shadcn/ui.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 1 — GIT BRANCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
git checkout -b feature/bronze-tier
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 2 — REPOSITORY STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scaffold this EXACT directory layout. Do not deviate.

```
hac0-ai-employee/
│
├── .claude/
│   ├── mcp.json                          # Context7 + filesystem MCP config
│   └── skills/
│       ├── vault-setup/                  # (copy from bronze-tier-skills/)
│       ├── gmail-watcher/
│       ├── file-processor/
│       ├── dashboard-updater/
│       └── company-handbook/
│
├── frontend/                             # Next.js 15 App Router
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                      # Dashboard home
│   │   ├── globals.css
│   │   ├── dashboard/
│   │   │   └── page.tsx                  # Live dashboard view
│   │   ├── needs-action/
│   │   │   └── page.tsx                  # /Needs_Action items list
│   │   ├── pending-approval/
│   │   │   └── page.tsx                  # Approval queue
│   │   └── handbook/
│   │       └── page.tsx                  # Company Handbook viewer/editor
│   ├── components/
│   │   ├── ui/                           # shadcn/ui components
│   │   ├── StatusCard.tsx
│   │   ├── ActionItem.tsx
│   │   ├── ApprovalCard.tsx
│   │   └── ActivityFeed.tsx
│   ├── lib/
│   │   └── api.ts                        # Typed fetch wrapper for FastAPI
│   ├── public/
│   ├── .env.local                        # NEXT_PUBLIC_API_URL=http://localhost:8000
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── components.json                   # shadcn config
│   └── package.json
│
├── backend/                              # FastAPI + Python 3.13
│   ├── app/
│   │   ├── main.py                       # FastAPI app entry point
│   │   ├── config.py                     # Settings (pydantic BaseSettings)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── vault.py                  # GET /vault/status
│   │   │   ├── needs_action.py           # GET /needs-action, POST /needs-action/process
│   │   │   ├── approvals.py              # GET /approvals, POST /approvals/{id}/approve|reject
│   │   │   ├── dashboard.py              # GET /dashboard, POST /dashboard/refresh
│   │   │   └── handbook.py               # GET /handbook, PUT /handbook
│   │   ├── services/
│   │   │   ├── vault_service.py          # Vault read/write operations
│   │   │   ├── file_processor.py         # Port of file-processor skill logic
│   │   │   └── dashboard_service.py      # Port of dashboard-updater skill logic
│   │   └── models/
│   │       ├── action_item.py            # Pydantic models
│   │       ├── approval.py
│   │       └── dashboard.py
│   ├── watchers/
│   │   ├── base_watcher.py               # Abstract BaseWatcher class
│   │   ├── gmail_watcher.py              # Port of gmail-watcher skill script
│   │   └── filesystem_watcher.py         # Filesystem drop watcher
│   ├── .env                              # VAULT_PATH, GMAIL_*, DRY_RUN
│   ├── pyproject.toml                    # UV project config
│   └── requirements.txt
│
├── vault/                                # The Obsidian vault (local data)
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── In_Progress/
│   ├── Plans/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Rejected/
│   ├── Done/
│   ├── Logs/
│   ├── Briefings/
│   ├── Accounting/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   └── Business_Goals.md
│
├── .env.example                          # Template — never commit real .env
├── .gitignore                            # From vault-setup skill assets
├── docker-compose.yml                    # Optional: run backend as service
└── README.md
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 3 — VAULT INITIALIZATION (vault-setup skill)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apply the vault-setup skill:

1. Run `python .claude/skills/vault-setup/scripts/init_vault.py \
     --vault ./vault \
     --owner "Your Name" \
     --business "Your Business"`

2. Verify all folders exist: Inbox, Needs_Action, In_Progress, Plans,
   Pending_Approval, Approved, Rejected, Done, Logs, Briefings, Accounting

3. Verify Dashboard.md, Company_Handbook.md, Business_Goals.md are created

4. Place the `.gitignore` from `vault-setup/assets/gitignore-template.txt`
   at the project root

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 4 — BACKEND: FastAPI (Python 3.13 + UV)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use Context7 to fetch FastAPI and Pydantic v2 docs before implementing.

### 4A — Project Setup

```bash
cd backend
uv init
uv add fastapi uvicorn[standard] pydantic pydantic-settings \
        python-dotenv python-frontmatter watchdog \
        google-auth google-auth-oauthlib google-auth-httplib2 \
        google-api-python-client
```

### 4B — config.py

Use `pydantic-settings` BaseSettings. Load from `.env`:

```python
class Settings(BaseSettings):
    vault_path: Path = Path("../vault")
    gmail_credentials_path: Path = Path("../credentials.json")
    gmail_token_path: Path = Path("../token.json")
    gmail_poll_interval: int = 120
    gmail_query: str = "is:unread is:important"
    dry_run: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env")
```

### 4C — Pydantic Models

**ActionItem** (`models/action_item.py`):
```python
class ActionItem(BaseModel):
    id: str                  # filename without extension
    filename: str
    type: str                # email | whatsapp | file_drop
    sender: str
    subject: str
    received: datetime
    priority: Literal["high", "medium", "low"]
    status: str
    age_hours: float         # computed: now - received
```

**ApprovalRequest** (`models/approval.py`):
```python
class ApprovalRequest(BaseModel):
    id: str
    filename: str
    action: str
    source_file: str
    created: datetime
    expires: datetime
    status: str
    priority: str
    is_overdue: bool         # computed: expires < now
```

**DashboardStatus** (`models/dashboard.py`):
```python
class DashboardStatus(BaseModel):
    last_updated: datetime
    needs_action_count: int
    pending_approval_count: int
    plans_count: int
    done_today_count: int
    mtd_revenue: str
    monthly_target: str
    alerts: list[str]
    recent_activity: list[str]
```

### 4D — Vault Service (`services/vault_service.py`)

Implement these functions using logic from the file-processor skill:

```python
def list_action_items(vault_path: Path) -> list[ActionItem]
def list_approvals(vault_path: Path) -> list[ApprovalRequest]
def process_action_item(vault_path: Path, filename: str) -> dict
def approve_item(vault_path: Path, filename: str) -> dict
def reject_item(vault_path: Path, filename: str) -> dict
def get_handbook(vault_path: Path) -> str
def update_handbook(vault_path: Path, content: str) -> dict
def get_dashboard_status(vault_path: Path) -> DashboardStatus
def refresh_dashboard(vault_path: Path) -> dict
```

Use `python-frontmatter` to parse YAML frontmatter from vault `.md` files.
Apply routing rules from `file-processor/references/routing-rules.md`.
Apply lock pattern from `dashboard-updater` skill before writing Dashboard.md.

### 4E — API Routers

**GET  /api/vault/status**         → folder counts, vault health check
**GET  /api/needs-action**         → list[ActionItem], sorted by priority then age
**POST /api/needs-action/process** → body: `{filename: str}` → trigger file-processor
**POST /api/needs-action/process-all** → process all pending items
**GET  /api/approvals**            → list[ApprovalRequest], overdue flagged
**POST /api/approvals/{id}/approve** → move to /Approved
**POST /api/approvals/{id}/reject**  → move to /Rejected
**GET  /api/dashboard**            → DashboardStatus
**POST /api/dashboard/refresh**    → run dashboard-updater, return updated status
**GET  /api/handbook**             → raw markdown string
**PUT  /api/handbook**             → body: `{content: str}` → save handbook
**GET  /api/health**               → `{status: "ok", vault_path: str, timestamp: str}`

Enable CORS for `http://localhost:3000`.
Add response models and HTTP 404/500 error handlers.

### 4F — Gmail Watcher Integration

Port `gmail-watcher/scripts/gmail_watcher.py` into `watchers/gmail_watcher.py`.
Run it as a background task on FastAPI startup using `asyncio.create_task()`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_gmail_watcher_async())
    yield
    task.cancel()
```

Only start the watcher if `GMAIL_CREDENTIALS_PATH` exists and is valid.
If credentials are missing, log a warning and skip — do not crash the API.

### 4G — Filesystem Watcher

Port `watchers/filesystem_watcher.py` using the `watchdog` library.
Watch `vault/Inbox/` for new file drops.
On new file → create `FILE_<name>.md` in `vault/Needs_Action/`.
Run as a second background task in lifespan.

### 4H — main.py

```python
app = FastAPI(
    title="HAC0 AI Employee API",
    description="Bronze Tier Personal AI Employee — Local-first agent backend",
    version="0.1.0",
    lifespan=lifespan,
)
# Mount all routers with prefix /api
# Add CORS middleware
# Add /api/health endpoint
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 5 — FRONTEND: Next.js 15 App Router
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use Context7 to fetch Next.js 15 App Router, Tailwind v4, and shadcn/ui docs
before implementing.

### 5A — Project Setup

```bash
cd frontend
npx create-next-app@latest . \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir=false \
  --import-alias="@/*"

npx shadcn@latest init
npx shadcn@latest add card badge button table tabs alert separator
```

Set `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5B — API Client (`lib/api.ts`)

Typed fetch wrapper — all calls go through this:

```typescript
const BASE = process.env.NEXT_PUBLIC_API_URL

export async function fetchDashboard(): Promise<DashboardStatus>
export async function fetchNeedsAction(): Promise<ActionItem[]>
export async function processItem(filename: string): Promise<void>
export async function processAll(): Promise<void>
export async function fetchApprovals(): Promise<ApprovalRequest[]>
export async function approveItem(id: string): Promise<void>
export async function rejectItem(id: string): Promise<void>
export async function fetchHandbook(): Promise<string>
export async function updateHandbook(content: string): Promise<void>
export async function refreshDashboard(): Promise<DashboardStatus>
```

### 5C — Types (`lib/types.ts`)

Mirror the Pydantic models exactly:

```typescript
interface ActionItem {
  id: string
  filename: string
  type: "email" | "whatsapp" | "file_drop"
  sender: string
  subject: string
  received: string
  priority: "high" | "medium" | "low"
  status: string
  age_hours: number
}

interface ApprovalRequest {
  id: string
  filename: string
  action: string
  source_file: string
  created: string
  expires: string
  status: string
  priority: string
  is_overdue: boolean
}

interface DashboardStatus {
  last_updated: string
  needs_action_count: number
  pending_approval_count: number
  plans_count: number
  done_today_count: number
  mtd_revenue: string
  monthly_target: string
  alerts: string[]
  recent_activity: string[]
}
```

### 5D — Components

**StatusCard.tsx**
- Props: `title`, `value`, `icon`, `variant?: "default"|"warning"|"danger"`
- Use shadcn Card + Badge
- Show warning color when value > 0 for pending items

**ActionItem.tsx**
- Shows one Needs_Action item
- Priority badge (red=high, yellow=medium, gray=low)
- Age display: "2h ago", "5m ago"
- "Process" button → calls `processItem(filename)` → optimistic update

**ApprovalCard.tsx**
- Shows one approval request
- Overdue badge (red) if `is_overdue`
- "Approve ✅" and "Reject ❌" buttons
- Confirm dialog before approve/reject
- Optimistic removal from list on action

**ActivityFeed.tsx**
- Props: `activities: string[]`
- Renders last 20 activity log entries
- Auto-scroll to newest
- Timestamp formatting

### 5E — Pages

**`app/page.tsx`** — redirects to `/dashboard`

**`app/dashboard/page.tsx`** — Main Dashboard
- Server component that fetches `DashboardStatus` on load
- Status grid: 4 StatusCards (Needs Action, Awaiting Approval, Done Today, Active Plans)
- Revenue row: MTD vs Target
- Alerts section: yellow alert boxes for each alert string
- ActivityFeed component with recent_activity
- "Refresh Dashboard" button → POST /api/dashboard/refresh → re-renders
- Auto-refresh every 30 seconds using `useInterval`

**`app/needs-action/page.tsx`** — Action Items
- Client component
- Table of ActionItems sorted by priority → age
- "Process All" button at top
- Empty state: "✅ All clear — no pending items"
- Loading skeleton

**`app/pending-approval/page.tsx`** — Approval Queue
- Client component
- List of ApprovalCards
- Overdue items float to top
- Empty state: "Nothing awaiting your approval"
- Count badge in nav

**`app/handbook/page.tsx`** — Company Handbook
- Split view: rendered markdown (left) + raw editor (textarea, right)
- "Save Changes" button → PUT /api/handbook
- Unsaved changes warning on navigation
- Read-only rendered view uses `react-markdown`

### 5F — Layout (`app/layout.tsx`)

Sidebar navigation with:
- 🤖 AI Employee (logo/home)
- 📊 Dashboard
- 📋 Needs Action (+ badge with count)
- ⏳ Pending Approval (+ badge with count, red if overdue)
- 📖 Handbook

Use shadcn `Separator` between sections.
Show connection status dot (green/red) by polling `/api/health` every 10s.
Dark mode support via Tailwind.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 6 — COMPANY HANDBOOK (company-handbook skill)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apply the company-handbook skill to populate `vault/Company_Handbook.md`:

1. Run `python .claude/skills/company-handbook/scripts/validate_handbook.py --fix`
2. Ensure all 8 required sections are present (see skill SKILL.md)
3. Set default payment threshold to $100
4. Set default priority keywords per the skill's General template
5. Verify via the validator — must exit with code 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 7 — WATCHER SETUP (gmail-watcher skill)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copy `gmail-watcher/scripts/gmail_watcher.py` into `backend/watchers/`.
Copy `filesystem_watcher.py` into `backend/watchers/`.

In `backend/.env` set:
```
VAULT_PATH=../vault
GMAIL_POLL_INTERVAL=120
GMAIL_QUERY=is:unread is:important
DRY_RUN=true           # Set false after OAuth credentials are configured
```

For local development without Gmail credentials, the watcher must run in
DRY_RUN=true mode by default — it should log mock activity without crashing.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 8 — FILE PROCESSOR WIRING (file-processor skill)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Port `file-processor/scripts/process_files.py` logic into
`backend/app/services/file_processor.py`.

The FastAPI endpoint `POST /api/needs-action/process` must:
1. Read `vault/Company_Handbook.md` for routing rules
2. Apply routing logic from `file-processor/references/routing-rules.md`
3. Create `PLAN_*.md` in `vault/Plans/`
4. Route approval items to `vault/Pending_Approval/`
5. Move source file to `vault/Done/`
6. Trigger a dashboard refresh
7. Return `{processed: filename, plan: plan_filename, requires_approval: bool}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 9 — DASHBOARD WIRING (dashboard-updater skill)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Port `dashboard-updater/scripts/update_dashboard.py` logic into
`backend/app/services/dashboard_service.py`.

The `POST /api/dashboard/refresh` endpoint must:
1. Acquire the write lock (`.dashboard_lock` file pattern from skill)
2. Count all vault folders
3. Extract revenue from `Business_Goals.md`
4. Detect alerts (overdue approvals, stale needs-action items)
5. Write `Dashboard.md` using the schema from `dashboard-updater/references/dashboard-schema.md`
6. Release the lock
7. Return the updated `DashboardStatus`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 10 — ENVIRONMENT & SECURITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Create `.env.example` at project root:
```
# Backend
VAULT_PATH=./vault
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json
GMAIL_POLL_INTERVAL=120
GMAIL_QUERY=is:unread is:important
DRY_RUN=true

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

NEVER commit real `.env` files. The `.gitignore` from vault-setup skill
must block: `.env`, `credentials.json`, `token.json`, `whatsapp_session/`.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 11 — README.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write a production-quality `README.md` covering:

1. **Project Overview** — What this is, what it does
2. **Architecture Diagram** — ASCII diagram showing:
   Gmail → gmail_watcher → vault/Needs_Action → FastAPI → Next.js Dashboard
3. **Tech Stack** — Next.js 15, FastAPI, Python 3.13, Obsidian vault, Context7 MCP
4. **Bronze Tier Deliverables Checklist** — with checkmarks for completed items
5. **Quick Start** (5 commands max):
   ```bash
   git clone ... && cd hac0-ai-employee
   cp .env.example .env          # edit VAULT_PATH
   cd backend && uv run uvicorn app.main:app --reload
   cd frontend && npm install && npm run dev
   # Open http://localhost:3000
   ```
6. **Gmail OAuth Setup** — link to `gmail-watcher/references/oauth-setup-guide.md`
7. **Skills Used** — table listing all 5 skills, their type, and purpose
8. **Folder Structure** — vault folder descriptions from vault-setup skill
9. **Extending to Silver Tier** — brief mention of what comes next

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 12 — VALIDATION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before marking Bronze Tier complete, verify ALL of the following:

### Vault (vault-setup skill)
- [ ] `vault/Dashboard.md` exists with correct schema
- [ ] `vault/Company_Handbook.md` exists with all 8 sections
- [ ] `vault/Business_Goals.md` exists
- [ ] All 11 folders exist in vault/
- [ ] `.gitignore` blocks credentials and `.env`

### Company Handbook (company-handbook skill)
- [ ] `python .claude/skills/company-handbook/scripts/validate_handbook.py` exits 0
- [ ] Payment threshold is defined
- [ ] Priority keywords are listed
- [ ] Autonomy thresholds table is present

### Backend (FastAPI)
- [ ] `uvicorn app.main:app --reload` starts without errors
- [ ] `GET /api/health` returns `{"status": "ok"}`
- [ ] `GET /api/vault/status` returns folder counts
- [ ] `GET /api/needs-action` returns empty list (no errors)
- [ ] `GET /api/approvals` returns empty list (no errors)
- [ ] `GET /api/dashboard` returns DashboardStatus
- [ ] `POST /api/dashboard/refresh` updates Dashboard.md and returns new status
- [ ] `GET /api/handbook` returns Company_Handbook.md content
- [ ] Filesystem watcher starts and watches vault/Inbox/
- [ ] Gmail watcher starts in DRY_RUN mode without crashing
- [ ] Drop a test file in vault/Inbox/ → verify FILE_*.md appears in vault/Needs_Action/
- [ ] Call `POST /api/needs-action/process` on that file → verify PLAN_*.md in vault/Plans/

### Frontend (Next.js)
- [ ] `npm run dev` starts without errors
- [ ] `npm run build` completes without TypeScript errors
- [ ] Dashboard page loads and shows StatusCards
- [ ] Needs Action page loads (empty state shown correctly)
- [ ] Pending Approval page loads (empty state shown correctly)
- [ ] Handbook page loads and renders Company_Handbook.md content
- [ ] Sidebar navigation works for all routes
- [ ] Connection status dot shows green when backend is running
- [ ] "Refresh Dashboard" button calls API and updates counts

### Skills (all 5)
- [ ] All 5 skill SKILL.md files are present in `.claude/skills/`
- [ ] All skill scripts run without import errors
- [ ] File-processor routing logic correctly routes payment items to /Pending_Approval
- [ ] Dashboard-updater correctly acquires and releases .dashboard_lock

### Git
- [ ] All changes committed on `feature/bronze-tier` branch
- [ ] No `.env`, `credentials.json`, `token.json`, or `node_modules` in git
- [ ] Commit message: `feat: complete Bronze Tier — vault, watchers, FastAPI, Next.js dashboard`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## CONSTRAINTS & RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **Skills first**: Always re-read the relevant SKILL.md before implementing
   that skill's functionality. Never implement from memory.

2. **Context7 for docs**: Before writing any Next.js, FastAPI, Pydantic, or
   shadcn code, resolve the library's current API via Context7 MCP.

3. **DRY_RUN=true default**: All scripts must default to dry-run mode.
   Never write, move, or delete vault files unless DRY_RUN=false is explicit.

4. **No credentials in git**: Hard block. If you ever write a file that
   contains an API key, token, or password — stop, remove it, add it to
   `.gitignore`, and move it to `.env`.

5. **Routing rules are sacred**: The file-processor must apply routing rules
   from `file-processor/references/routing-rules.md` exactly.
   Payment items → always `/Pending_Approval`. No exceptions.

6. **Single writer for Dashboard.md**: Use the `.dashboard_lock` pattern from
   the dashboard-updater skill. Never write Dashboard.md without the lock.

7. **Autonomy level**: This is Bronze Tier. Claude never sends emails, makes
   payments, or posts to social media. These are Silver/Gold tier features.
   Any code that would do this must be clearly gated behind approval.

8. **Fail gracefully**: If Gmail credentials are missing, the watcher logs a
   warning and exits cleanly. The API must still start. Frontend must still
   work without watchers running.

9. **Commit often**: Commit after each major step (vault setup, backend complete,
   frontend complete). Use conventional commits: `feat:`, `fix:`, `chore:`.

10. **Use UV for Python**: All Python dependency management uses UV, not pip
    directly. `uv add`, `uv run`, `uv sync`.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Begin with STEP 0. Do not skip any step. Do not ask for permission between
steps — work autonomously through the entire checklist. Report progress after
each step is complete.
