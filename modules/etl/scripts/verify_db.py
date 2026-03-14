#!/usr/bin/env uv run
"""
Script para verificar conexão Postgres e existência da tabela application_logs.
Execute dentro do container: docker compose exec celery_worker uv run python scripts/verify_db.py
Ou localmente (com Postgres rodando): uv run python scripts/verify_db.py
"""
from infra.database.postgres import get_connection


def main():
    print("Verificando conexão com PostgreSQL...")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = 'application_logs'
                    )
                    """
                )
                exists = cur.fetchone()[0]
                if exists:
                    cur.execute("SELECT COUNT(*) FROM application_logs")
                    count = cur.fetchone()[0]
                    print(f"OK: Tabela application_logs existe. Registros: {count}")
                else:
                    print("ERRO: Tabela application_logs NÃO existe.")
                    print("Solução: docker compose down -v && docker compose up -d")
                    print("(O volume postgres_etl_data precisa ser recriado para rodar os scripts init-db)")
    except Exception as e:
        print(f"ERRO ao conectar: {e}")
        raise


if __name__ == "__main__":
    main()
