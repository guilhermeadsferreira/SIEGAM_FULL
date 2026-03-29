.PHONY: up down stop ps logs logs-etl logs-notifications run-once seed clean rebuild

## Sobe toda a stack: db + redis + ETL worker + Notifications consumer
up:
	docker compose up --build -d

## Rebuild forçado sem cache (útil após mudanças em Dockerfile ou dependências)
rebuild:
	docker compose build --no-cache && docker compose up -d

## Derruba os containers (mantém volumes)
down:
	docker compose down

## Para os containers sem remover
stop:
	docker compose stop

## Status dos containers
ps:
	docker compose ps

## Logs de todos os serviços
logs:
	docker compose logs -f

## Logs do worker ETL
logs-etl:
	docker compose logs -f celery_worker

## Logs do consumer de notificações
logs-notifications:
	docker compose logs -f notifications

## Dispara o pipeline ETL manualmente (sem aguardar o schedule das 6h)
run-once:
	docker compose exec celery_worker uv run python run_once.py

## Aplica seed de dados de teste (requer psql local)
seed:
	psql postgresql://cempa:cempa@localhost:5432/sigedam -f init-db/seed_e2e.sql

## Remove containers e volumes (reset completo)
clean:
	docker compose down -v
