# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains two independent Python microservices for a meteorological alert pipeline:

- **`etl/`** — Downloads meteograms (CEMPA/UFG), transforms ASC files to JSON, analyzes weather data, persists alerts, and publishes to Redis queue.
- **`notifications/`** — Consumes Redis queue, resolves recipients, filters by user preferences, renders HTML/WhatsApp templates, dispatches via email/Z-API, and records delivery.

Pipeline: `CEMPA/UFG → ETL (Download→Transform→Analyze→Load) → PostgreSQL + Redis → Notifications (Consume→Resolve→Filter→Render→Dispatch)`

## Package Manager

Both modules use **UV** (not pip). Always use `uv run` to execute scripts inside the module directories.

```bash
uv run python main.py
uv run pytest
uv run celery worker ...
```

See `docs/UV.md` for UV-specific instructions.

## Running & Development

### ETL (Celery-based)

```bash
cd etl

# Docker (recommended)
make up          # Build and start all services (Redis, Postgres, Celery worker+beat)
make down        # Stop services
make logs        # Tail Celery worker logs
make verify-db   # Check Postgres connectivity

# Local (requires .env)
make worker      # Start Celery worker
make beat        # Start Celery beat scheduler
make worker-beat # Combined worker + beat

# Manual trigger
uv run python run_once.py  # Manually trigger download_file task
```

### Notifications (Consumer-based)

```bash
cd notifications

# Docker
docker compose up --build

# Local
uv run python main.py
```

### Tests (Notifications module only)

```bash
cd notifications
uv run pytest                          # All tests
uv run pytest tests/test_filter.py     # Single file
uv run pytest --cov                    # With coverage
```

## Architecture

Both modules follow Clean Architecture (DDD):

```
{module}/
├── domain/       # Entities, value objects, exceptions, protocols — no external deps
├── application/  # Use cases, orchestration — depends only on domain
├── infra/        # Concrete implementations (DB, Redis, HTTP, logger)
├── main.py       # Entrypoint
└── settings.py   # Pydantic Settings (loaded from .env)
```

**ETL-specific**: Celery tasks are defined in `etl/main.py`. Task chaining uses `.delay()` on success. Beat schedule runs daily at the configured hour.

**Notifications-specific**: Consumer uses `BLPOP` on `etl:notifications:ready` Redis key. Exceptions are classified as retryable or non-retryable with dead-letter queue support.

## Configuration

Each module has its own `.env` (copy from `.env.example`). Key variables:

| Module | Critical Vars |
|--------|---------------|
| ETL | `DATABASE_URL`, `REDIS_URL`, `METEOGRAM_BASE_URL`, `CELERY_SCHEDULE_HOUR` |
| Notifications | `DATABASE_URL`, `REDIS_URL`, `SMTP_*`, `ZAPI_*`, `FRONTEND_URL` |

## Key Integration Points

- Redis queue name between modules: `etl:notifications:ready`
- Both modules share the same PostgreSQL instance (Supabase in prod)
- WhatsApp via Z-API; email via SMTP (Gmail)
- Retry logic uses `tenacity` with exponential backoff throughout

## Open Decisions (check STATUS.md before making changes)

1. Temperature threshold filtering location (ETL vs Notifications)
2. Behavior when a polygon has no matching city
3. Idempotency constraint on `avisos` table
4. Graceful shutdown & health checks for the notification consumer
5. Rain alerts were disabled in legacy — confirm activation status before enabling
