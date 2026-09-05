# KhedutMitra AI - AI Agent Handoff

## Project
KhedutMitra AI is a multilingual farmer-market intelligence platform for Gujarat cotton and groundnut farmers. It helps farmers compare mandi prices, forecast prices, decide whether to sell or store, find buyers, track inventory, estimate profit, and receive AI-assisted guidance.

Repository: https://github.com/Darshitmehta293/Khedutmitra-ai
Current branch: `main`
Latest commit: `0bc3d4d Add landing page about and contact`
Developer: Darshit Mehta

## Workspace

```text
D:/test/khedutmitra-ai
  api/index.py                         Vercel Python entrypoint
  backend/app/main.py                  FastAPI application
  backend/app/api/                     API routers
  backend/app/agents/                  AI/business agents
  backend/app/services/                Market, forecast, quality, Granite services
  backend/app/models/models.py         SQLAlchemy models
  backend/app/schemas/schemas.py       Pydantic request/response schemas
  backend/app/database/session.py      Async SQLAlchemy engine/session
  backend/tests/test_agents.py         Agent/provider tests
  frontend/src/App.tsx                 React routes
  frontend/src/components/Layout.tsx   Authenticated app navigation
  frontend/src/pages/                  Frontend pages
  frontend/src/services/api.ts         Axios API client
  frontend/src/index.css               Tailwind/component CSS and night mode
  vercel.json                          Vercel build/function configuration
```

## Stack
- Backend: FastAPI, SQLAlchemy async, SQLite locally, PostgreSQL/asyncpg in production
- Frontend: React 18, TypeScript, Vite, Tailwind CSS, React Router, Axios
- AI: agent orchestration with optional IBM Granite; deterministic template fallback
- Auth: bcrypt password hashes and JWT tokens
- Deployment: Vercel frontend/build plus `api/index.py`; GitHub `main` branch
- Languages: English, Gujarati, Hindi

## Existing User Features

### Public
- Landing page with product description, demo CTA, About section, Contact section, and developer GitHub links
- Login, registration, and one-click demo login
- Language switcher
- Persistent light/night mode toggle

### Farmer
- Dashboard with inventory value, revenue scenarios, buyer opportunities, and recommendation summary
- Market prices across Gujarat mandis
- Historical price trends and baseline forecasts for 3/7/15/30 days
- Sell-or-store recommendation using market, forecast, storage, transport, quality-loss, and buyer factors
- Buyer matching and enquiry/offer creation
- Crop quality upload assessment using mock provider
- Income dashboard
- Multilingual AI assistant
- Local farm planner
- Inventory page with inventory lot create/archive and recommendation history
- Intelligence Hub at `/intelligence` with weather, demand, mandi net comparison, logistics estimate, storage facilities, negotiation range, price alerts, notifications, expenses, profit, risk advisor, schemes, market news, voice input, and cooperative status

### Buyer/Admin Foundations
- Buyer registration/profile
- Database-backed buyer listings and listing creation API
- Offer listing and offer status transitions with ownership checks
- Admin health, dashboard, and user APIs
- Admin analytics endpoint under Intelligence Hub API

## Important Backend Routes

Routers are mounted under `/api` in `backend/app/main.py`:
- `/api/auth`
- `/api/farmer`
- `/api/markets`
- `/api/ai`
- `/api/buyers`
- `/api/admin`
- `/api/intelligence`

Important intelligence endpoints:
- `GET /api/intelligence/weather`
- `GET /api/intelligence/demand`
- `GET /api/intelligence/mandi-comparison`
- `GET /api/intelligence/logistics`
- `GET /api/intelligence/storage`
- `POST /api/intelligence/negotiation`
- `GET/POST /api/intelligence/alerts`
- `GET /api/intelligence/notifications`
- `GET/PUT /api/intelligence/profile`
- `POST /api/intelligence/expenses`
- `GET /api/intelligence/profit`
- `GET /api/intelligence/risk`
- `GET /api/intelligence/schemes`
- `GET /api/intelligence/news`
- `POST /api/intelligence/ratings`
- `GET/POST /api/intelligence/cooperative`
- `GET /api/intelligence/explain/{recommendation_id}`
- `GET /api/intelligence/admin-analytics`

## Key Recent Commits

- `06b2f9a` Add local farm planner module
- `84b5571` Add persistent inventory and marketplace workflows
- `d11bbbb` Add farmer intelligence modules
- `c07098f` Fix PgBouncer prepared statements on Vercel
- `ee783f7` Use unique asyncpg statements with PgBouncer
- `d1a23b9` Harden authentication flow
- `1e737cd` Add persistent night mode
- `0bc3d4d` Add landing page about and contact

## Authentication Notes

Auth implementation:
- `backend/app/api/auth.py`
- `backend/app/core/security.py`
- `backend/app/api/deps.py`
- `frontend/src/context/AuthContext.tsx`

Demo credentials:
- Phone: `9876543210`
- Password: `demo1234`

Authentication fixes already made:
- Trim phone numbers on register/login
- Return `language` in register/login token responses
- Invalid/malformed bcrypt hashes return false instead of crashing
- JWT contains `sub`, `role`, `exp`, and `iat`
- Role guards: `require_farmer`, `require_buyer`, `require_admin`

## PostgreSQL/Vercel Fix

Vercel previously failed during startup with:

```text
asyncpg.exceptions.DuplicatePreparedStatementError
```

The fix is in `backend/app/database/session.py` and `backend/app/core/config.py`:
- PostgreSQL URLs become `postgresql+asyncpg`
- `prepared_statement_cache_size=0`
- asyncpg `statement_cache_size=0`
- unique asyncpg prepared-statement names using UUIDs
- `NullPool` when `VERCEL` is set or the URL indicates pooler/PgBouncer

If the error still appears in Vercel, confirm the deployment is using commit `ee783f7` or newer and redeploy the latest GitHub commit. A stale deployment is likely if the traceback still shows the old behavior.

## Vercel Configuration

`vercel.json` expects the project root to be the repository root, not `frontend`:

```json
{
  "framework": "vite",
  "buildCommand": "cd frontend && npm run build",
  "installCommand": "cd frontend && npm ci",
  "outputDirectory": "frontend/dist",
  "functions": { "api/index.py": { "maxDuration": 60 } }
}
```

Required production environment variables include:
- `DATABASE_URL` pointing to persistent PostgreSQL
- `JWT_SECRET`
- `DEMO_MODE`
- Optional IBM Granite variables
- Optional live market provider variables

## Current Data/Provider Reality

Several features are intentionally deterministic/demo-backed because credentials/providers are unavailable:
- Market data defaults to `MockMarketDataProvider`
- AGMARKNET-compatible adapter exists but endpoint/schema is not configured
- Forecasts use a baseline model
- Buyer matching falls back to demo buyers when no database listings exist
- Quality assessment uses mock provider
- Weather, demand, logistics, storage, schemes, and news in Intelligence Hub use deterministic fallback data
- Voice input uses browser Web Speech API when supported
- Notifications are in-app alert records; no SMS/WhatsApp/email delivery exists
- IBM Granite falls back to templates when credentials are absent

Never present demo data as live data. Preserve `is_demo` and source/disclaimer fields.

## Validation Commands

From `D:/test/khedutmitra-ai/frontend`:

```powershell
npm run build
npm run lint
```

`npm run build` has passed after the latest frontend changes. `npm run lint` may fail if eslint is not installed in the environment.

From `D:/test/khedutmitra-ai/backend`:

```powershell
& D:/test/.venv/Scripts/python.exe -m py_compile app/main.py
& D:/test/.venv/Scripts/python.exe -m pytest -q
```

The active local virtual environment previously lacked `pytest` and `asyncpg`. Use the project requirements or the repository root `requirements.txt` when installing missing dependencies. SQLite can be used for local auth smoke tests by clearing inherited `VERCEL` and setting:

```powershell
$env:VERCEL = $null
$env:DATABASE_URL = 'sqlite+aiosqlite:///./auth-smoke.db'
```

Useful auth smoke checks:
- hash and verify correct password
- reject wrong password
- reject malformed hash without exception
- create/decode JWT
- serialize `TokenResponse` with language

## Known Incomplete or Provider-Dependent Areas

These are not fully production-grade and should be handled honestly:
- Buyer-facing frontend dashboard/listing management is not complete
- Deal/contract model exists but full deal UI and delivery workflow are not complete
- Expense tracking has create/profit summary but no complete expense history/edit/delete UI
- Ratings have create API but no complete rating UI/history/aggregation
- Cooperative model has create/status foundation but no multi-farmer invitation/join UI or true bulk selling workflow
- Weather/news/government schemes are fallback data without live providers
- Price alerts are persisted and visible in-app but have no background scheduler or external notification channel
- Quality assessments are not yet persisted through the quality endpoint
- Chat conversations are not yet persisted/reloaded from Conversation/Message models
- Admin analytics has API foundation but no admin frontend page
- `create_tables()` is a lightweight startup initializer, not a migration system; production schema changes should use Alembic

Do not mark any of these as fully complete without adding the missing API, UI, validation, and tests.

## Recommended Next Work

1. Verify Vercel deployment is running latest commit and test `/api/health` and `/api/auth/login`.
2. Install missing backend dependencies and add API tests for register/login, role guards, and duplicate phone handling.
3. Add Alembic migrations for all added tables instead of relying on `create_all()` in production.
4. Add buyer dashboard, listing edit/deactivate, offer inbox, counter-offer, and deal completion workflow.
5. Persist chat and quality assessment records.
6. Add complete expense history and sales/deal ledger UI.
7. Add provider interfaces/configuration for weather, live market, transport, storage, news, and government schemes.
8. Keep all demo fallbacks explicit with source, timestamp, `is_demo`, and disclaimers.

## Working Rules for the Next AI Agent

- The user has granted full permission to continue development without repeated approval prompts.
- Work in small vertical slices: data model, API, frontend access, validation, tests, then commit/push.
- Do not leave a feature as only a label or stub endpoint.
- Do not revert unrelated user changes.
- Do not commit secrets or invent private contact information.
- Use ASCII by default in code/docs unless existing content requires Unicode.
- Do not claim Vercel deployment succeeded unless deployment status is actually verified.
