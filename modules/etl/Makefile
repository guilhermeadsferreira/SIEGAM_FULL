.PHONY: up run-once down logs verify-db worker beat worker-beat worker-docker beat-docker

## Sobe os containers (build + up)
up:
	docker compose up --build -d

## Executa o run_once.py dentro do container do worker
run-once:
	docker compose exec celery_worker uv run python run_once.py

## Derruba os containers
down:
	docker compose down

## Mostra logs do worker (opcional, útil em debug)
logs:
	docker compose logs -f celery_worker

## Verifica se Postgres está acessível e tabela application_logs existe
verify-db:
	docker compose exec celery_worker uv run python scripts/verify_db.py

## Roda Celery Worker localmente
worker:
	uv run celery --app main worker --loglevel=info

## Roda Celery Beat localmente
beat:
	uv run celery --app main beat --loglevel=info

## Roda Celery Worker e Beat juntos localmente
worker-beat:
	uv run celery --app main worker --beat --loglevel=info
