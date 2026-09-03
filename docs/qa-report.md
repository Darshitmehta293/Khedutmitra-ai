# KhedutMitra AI QA Report

Date: 2026-09-03

## Overall Status

**NOT READY** for production demo until a persistent hosted database is configured and the Docker/Postgres/Redis stack is verified. The local critical browser flow is working.

## Environment

- Frontend: Vite + React, local dev server on `http://127.0.0.1:3000`
- Backend: FastAPI/Uvicorn on `http://127.0.0.1:8000`
- Database tested locally: SQLite
- Python: 3.13 local QA environment; Vercel logs show Python 3.12
- Docker: unavailable in the QA environment

## Tests Passed

- Frontend production build: `npm run build`
- Backend module syntax: `python -m py_compile app/api/auth.py app/api/deps.py app/core/config.py app/schemas/schemas.py`
- Backend startup with SQLite
- `GET /api/health`
- Invalid login validation: 9-digit phone returns 422
- Demo login: `9876543210 / demo1234`
- Authenticated `GET /api/auth/me`
- New farmer registration through the live browser UI
- Authenticated dashboard load
- Authenticated inventory list and inventory creation
- Invalid JWT rejection: 401
- Market list and crop list APIs
- Sell-or-store recommendation API
- Live browser route matrix: dashboard, market, sell/store, buyers, quality, income, AI
- Desktop logout returns to landing page
- Gujarati-to-English language switch in browser
- Browser console had only React Router future-flag warnings during the tested flow

## Bugs Found and Fixed

### Empty Vercel environment values
Pydantic rejected empty integer and boolean environment variables. Empty values are now ignored and defaults are applied.

### Vercel SQLite path
The default relative SQLite path was read-only on Vercel. Vercel fallback now uses `/tmp/khedutmitra.db`.

### Demo login provisioning
The demo account was not present on an unseeded deployment. Demo mode now provisions the documented farmer account on login and can recover it for a valid demo session.

### Demo login import error
The demo provisioning path referenced `Language` without importing it. The missing import was added.

### Registration flow
The frontend discarded the registration token and sent empty optional email values. Registration now omits empty optional fields, stores the returned token, and routes directly to the dashboard.

### Auth refresh redirect
Protected routes redirected to login before local storage authentication hydration completed. Protected routes now wait for initialization, so refresh navigation preserves the session.

### IBM dependency resolution
The root Vercel dependency set was flattened and optional IBM SDK dependencies were removed from the Vercel runtime list to avoid incompatible `uv` resolution. Full backend requirements remain available for Docker deployments.

## Blocked or Not Fully Tested

- Docker Compose integration could not run because Docker is not installed in the QA environment.
- PostgreSQL and Redis integration was not executed locally.
- Persistent production registration/login was not verified. Vercel `/tmp` SQLite is temporary; configure hosted PostgreSQL using `DATABASE_URL` for real accounts.
- Pytest could not run because `pytest` is not installed in the base local interpreter.
- External IBM Granite, IBM COS, live market provider, and production AI credentials were not available.
- Full buyer registration, offer acceptance/rejection, concurrent offer behavior, and cross-user authorization require broader seeded integration fixtures.
- Image upload boundary tests and mobile visual screenshot checks were not fully completed.

## Commands Run

```text
cd frontend && npm run build
python -m py_compile app/api/auth.py app/api/deps.py app/core/config.py app/schemas/schemas.py
python -m app.database.seed
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Live HTTP and browser tests were run against the local servers. Docker and pytest were unavailable in the environment.

## Deployment Notes

Set these Vercel variables to valid values, not empty strings:

```text
DEMO_MODE=true
MAX_UPLOAD_SIZE_MB=5
JWT_EXPIRY_HOURS=24
BCRYPT_ROUNDS=12
ENABLE_QUALITY_AI=false
ENABLE_LIVE_MARKET_DATA=false
```

For persistent user accounts, set `DATABASE_URL` and `SYNC_DATABASE_URL` to a hosted PostgreSQL database. Do not rely on SQLite `/tmp` for production data.
