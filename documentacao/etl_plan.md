# ETL Plan — Novas Responsabilidades

> Especificação técnica para implementação das responsabilidades que migram do `modulo_alertas` legado para o `modules/etl`.
>
> **Referências:** `analise_modulo_envios.md`, `tasks.md`

---

## Contexto

O ETL passa a ser auto-suficiente para o pipeline meteorológico. Ele não faz mais chamadas HTTP ao `modulo_usuarios` durante a execução — busca `eventos` e `cidades` do seu próprio banco PostgreSQL e persiste `avisos` localmente. Ao final do pipeline, publica um evento no Redis para o módulo de notificações.

**Pipeline completo após a refatoração:**

```
[Task 1] download_file   ← já existe
         ↓
[Task 2] transform       ← já existe
         ↓
[Task 3] analyze         ← já existe (ajuste pendente no TemperatureAnalyzer — ver tasks.md)
         ↓
[Task 4] load            ← nova task
         ↓
[Task 5] dispatch        ← nova task
```

---

## Estrutura de Arquivos (delta)

```
modules/etl/
├── application/
│   └── load.py                              ← novo
├── domain/
│   ├── constants.py                         ← atualizar (novos nomes de task)
│   └── entities.py                          ← atualizar (adicionar AvisoRecord)
├── infra/
│   └── database/
│       ├── __init__.py                      ← atualizar (exportar novos repos)
│       ├── aviso_repository.py              ← novo
│       ├── cidade_repository.py             ← novo
│       └── evento_repository.py             ← novo
├── init-db/
│   ├── schema.sql                           ← sem alteração (tabelas já existem)
│   └── seed.sql                             ← novo (dados iniciais de eventos e cidades)
└── main.py                                  ← atualizar (tasks load e dispatch)
```

---

## 1. Seed de Dados — `init-db/seed.sql`

O ETL tem seu próprio banco com as tabelas `eventos` e `cidades` (já declaradas no `schema.sql`), mas sem dados. Esses dados são estáveis e gerenciados por migration — sem necessidade de sincronização com `modulo_usuarios` em tempo de execução.

### Por que seed e não HTTP?

- `eventos` são os tipos de fenômenos monitorados — mudam raramente e são definidos pelo domínio meteorológico, não pelos usuários
- `cidades` são os 246 municípios de Goiás — dados geográficos estáticos
- Seed via SQL garante que o ETL inicialize corretamente mesmo sem o `modulo_usuarios` disponível

### Conteúdo do seed

```sql
-- init-db/seed.sql
-- Idempotente: ON CONFLICT DO NOTHING garante segurança em re-execuções

INSERT INTO eventos (id, nome_evento, personalizavel, horario) VALUES
    (gen_random_uuid(), 'temperatura alta',  true, NOW()),
    (gen_random_uuid(), 'temperatura baixa', true, NOW()),
    (gen_random_uuid(), 'umidade baixa',     true, NOW()),
    (gen_random_uuid(), 'vento',             true, NOW()),
    (gen_random_uuid(), 'chuva',             true, NOW())
ON CONFLICT (nome_evento) DO NOTHING;

-- Cidades: todos os 246 municípios goianos
-- (espelhado de modulo_usuarios/src/main/resources/import.sql)
INSERT INTO cidades (id, nome) VALUES
    (gen_random_uuid(), 'Abadia de Goiás'),
    (gen_random_uuid(), 'Abadiânia'),
    -- ... 244 municípios restantes
ON CONFLICT (nome) DO NOTHING;
```

> **Atenção:** O `schema.sql` precisa de `UNIQUE` constraints em `eventos(nome_evento)` e `cidades(nome)` para o `ON CONFLICT` funcionar. Adicionar junto com o seed.

**Alteração no `schema.sql`:**

```sql
-- Adicionar após a declaração das tabelas:
ALTER TABLE eventos ADD CONSTRAINT uq_eventos_nome UNIQUE (nome_evento);
ALTER TABLE cidades ADD CONSTRAINT uq_cidades_nome UNIQUE (nome);
```

---

## 2. Repositórios — `infra/database/`

Seguindo o padrão já estabelecido em `application_log_repository.py`: funções simples usando `get_connection()`.

### `infra/database/evento_repository.py`

```python
"""Repositório de leitura de eventos do banco ETL."""

from __future__ import annotations

from infra.database.postgres import get_connection


def find_all() -> list[dict]:
    """
    Retorna todos os eventos cadastrados.
    Resultado: [{"id": "uuid-str", "nome_evento": "temperatura alta"}, ...]
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome_evento FROM eventos ORDER BY nome_evento")
            rows = cur.fetchall()
    return [{"id": str(row[0]), "nome_evento": row[1]} for row in rows]
```

### `infra/database/cidade_repository.py`

```python
"""Repositório de leitura de cidades do banco ETL."""

from __future__ import annotations

from infra.database.postgres import get_connection


def find_all() -> list[dict]:
    """
    Retorna todas as cidades cadastradas.
    Resultado: [{"id": "uuid-str", "nome": "Goiânia"}, ...]
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome FROM cidades ORDER BY nome")
            rows = cur.fetchall()
    return [{"id": str(row[0]), "nome": row[1]} for row in rows]
```

### `infra/database/aviso_repository.py`

```python
"""Repositório de inserção de avisos no banco ETL."""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from uuid import UUID

from psycopg.types.json import Jsonb

from infra.database.postgres import get_connection


def insert_batch(avisos: list[dict]) -> int:
    """
    Insere um lote de avisos na tabela `avisos`.
    Retorna o número de registros inseridos.

    Cada item do lote deve ter:
        id_evento (str UUID), id_cidade (str UUID),
        valor (float), valor_limite (float | None),
        diferenca (float), unidade_medida (str),
        data_geracao (str YYYY-MM-DD), data_referencia (str YYYY-MM-DD),
        horario (str HH:MM | None), segundos (float | None)
    """
    if not avisos:
        return 0

    rows = [
        (
            UUID(a["id_evento"]),
            UUID(a["id_cidade"]),
            Decimal(str(a["valor"])),
            Decimal(str(a["valor_limite"])) if a.get("valor_limite") is not None else None,
            Decimal(str(a["diferenca"])),
            a["unidade_medida"],
            date.fromisoformat(a["data_geracao"]),
            date.fromisoformat(a["data_referencia"]),
            time.fromisoformat(a["horario"]) if a.get("horario") else None,
            Decimal(str(a["segundos"])) if a.get("segundos") is not None else None,
        )
        for a in avisos
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO avisos
                    (id_evento, id_cidade, valor, valor_limite, diferenca,
                     unidade_medida, data_geracao, data_referencia, horario, segundos)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
    return len(rows)
```

### Atualizar `infra/database/__init__.py`

```python
from infra.database.application_log_repository import insert as insert_application_log
from infra.database.aviso_repository import insert_batch as insert_avisos
from infra.database.cidade_repository import find_all as find_all_cidades
from infra.database.evento_repository import find_all as find_all_eventos

__all__ = [
    "insert_application_log",
    "insert_avisos",
    "find_all_cidades",
    "find_all_eventos",
]
```

---

## 3. Serviço de Load — `application/load.py`

Responsável por toda a lógica de negócio da `Task 4`:
1. Carregar o catálogo de eventos e cidades do banco
2. Normalizar nomes para fazer o match polygon → cidade
3. Montar o payload de avisos
4. Persistir no banco

```python
"""Serviço de carga de avisos no banco ETL."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any

from infra.database import find_all_cidades, find_all_eventos, insert_avisos
from infra.logger import JsonLogger
from domain.exceptions import NonRetryableException
from domain.value_objects import Date


def _normalize(name: str) -> str:
    """
    Normaliza nome para comparação: remove acentos, lowercase, strip.
    Ex: 'Goiânia' → 'goiania', 'GOIÂNIA ' → 'goiania'
    """
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = nfkd.encode("ASCII", "ignore").decode("ASCII")
    return ascii_str.lower().strip()


@dataclass
class LoadResult:
    avisos_built: int
    avisos_inserted: int
    unmatched_polygons: list[str]
    unmatched_events: list[str]


class LoadService:

    def __init__(self, logger: JsonLogger):
        self._logger = logger
        self._evento_map: dict[str, str] = {}   # nome_evento → UUID str
        self._cidade_map: dict[str, str] = {}   # nome_normalizado → UUID str

    def _build_catalogs(self) -> None:
        """
        Carrega eventos e cidades do banco ETL e constrói
        os dicionários de lookup usados no mapeamento.
        """
        eventos = find_all_eventos()
        if not eventos:
            raise NonRetryableException(
                "Tabela 'eventos' está vazia — execute o seed antes de rodar o ETL."
            )
        self._evento_map = {e["nome_evento"]: e["id"] for e in eventos}

        cidades = find_all_cidades()
        if not cidades:
            raise NonRetryableException(
                "Tabela 'cidades' está vazia — execute o seed antes de rodar o ETL."
            )
        self._cidade_map = {_normalize(c["nome"]): c["id"] for c in cidades}

        self._logger.info(
            "Catálogos carregados",
            eventos=len(self._evento_map),
            cidades=len(self._cidade_map),
        )

    def _resolve_cidade(self, polygon_name: str) -> str | None:
        """
        Resolve polygon_name do CEMPA para o UUID da cidade no banco ETL.
        A normalização remove acentos e caixa, tornando o match robusto.
        """
        return self._cidade_map.get(_normalize(polygon_name))

    def _resolve_evento(self, alert_type: str) -> str | None:
        """
        Resolve o tipo de alerta do ETL para o UUID do evento no banco ETL.
        Os tipos do ETL e os nomes do banco devem ser idênticos (snake_case + espaços).
        """
        return self._evento_map.get(alert_type)

    def _build_aviso(
        self,
        alert: dict[str, Any],
        id_evento: str,
        id_cidade: str,
        today: str,
    ) -> dict:
        return {
            "id_evento": id_evento,
            "id_cidade": id_cidade,
            "valor": alert["value"],
            "valor_limite": alert.get("threshold"),
            "diferenca": alert.get("difference") or 0.0,
            "unidade_medida": alert["unit"],
            "data_geracao": today,
            "data_referencia": alert.get("date", today),
            "horario": _seconds_to_time(alert.get("seconds")),
            "segundos": alert.get("seconds"),
        }

    def process(self, analyze_results: dict[str, dict[str, Any]]) -> LoadResult:
        """
        Recebe o resultado da task 'analyze' e persiste os avisos no banco.

        analyze_results formato:
            { "Goiania": { "temperatura alta": {Alert dataclass fields}, ... }, ... }
        """
        self._build_catalogs()

        today = Date.get_current_date()
        avisos_to_insert: list[dict] = []
        unmatched_polygons: list[str] = []
        unmatched_events: list[str] = []

        for polygon_name, alerts_by_type in analyze_results.items():
            id_cidade = self._resolve_cidade(polygon_name)
            if not id_cidade:
                unmatched_polygons.append(polygon_name)
                self._logger.warning(
                    "Polígono sem correspondência de cidade",
                    polygon=polygon_name,
                )
                continue

            for alert_type, alert in alerts_by_type.items():
                id_evento = self._resolve_evento(alert_type)
                if not id_evento:
                    unmatched_events.append(alert_type)
                    self._logger.warning(
                        "Tipo de alerta sem correspondência de evento",
                        alert_type=alert_type,
                        polygon=polygon_name,
                    )
                    continue

                aviso = self._build_aviso(alert, id_evento, id_cidade, today)
                avisos_to_insert.append(aviso)

        inserted = insert_avisos(avisos_to_insert)

        self._logger.info(
            "Avisos persistidos",
            total_built=len(avisos_to_insert),
            total_inserted=inserted,
            unmatched_polygons=unmatched_polygons,
            unmatched_events=list(set(unmatched_events)),
        )

        return LoadResult(
            avisos_built=len(avisos_to_insert),
            avisos_inserted=inserted,
            unmatched_polygons=unmatched_polygons,
            unmatched_events=list(set(unmatched_events)),
        )


def _seconds_to_time(seconds: float | None) -> str | None:
    """Converte segundos do dia (ex: 39600) para 'HH:MM'."""
    if seconds is None:
        return None
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    return f"{h:02d}:{m:02d}"
```

---

## 4. Atualizar `domain/entities.py`

Adicionar o `AvisoRecord` para representar os dados que serão publicados no evento Redis (Task 5), com apenas dados de domínio meteorológico — sem UUIDs do `modulo_usuarios`.

```python
# domain/entities.py — adicionar ao final do arquivo

@dataclass(slots=True)
class AvisoRecord:
    """Representação de um aviso gerado e persistido pelo ETL.
    Publicado no evento Redis para o módulo de notificações."""
    polygon_name: str
    alert_type: AlertType
    value: float
    unit: str
    threshold: Optional[float]
    difference: Optional[float]
    seconds: Optional[float]
    date: str
```

---

## 5. Atualizar `domain/constants.py`

```python
# domain/constants.py

TASK_NAME_ETL      = "etl"
TASK_NAME_LOAD     = "load"       # nova
TASK_NAME_DISPATCH = "dispatch"   # nova

STATUS_STARTED     = "STARTED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_SUCCESS     = "SUCCESS"
STATUS_ERROR       = "ERROR"

REDIS_NOTIFICATIONS_QUEUE = "etl:notifications:ready"   # nova
```

---

## 6. Atualizar `main.py` — Tasks `load` e `dispatch`

### Task `load` (encadeada após `analyze`)

```python
@app.task(
    bind=True,
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def load(self, analyze_output: dict, execution_id=None):
    """
    Task 4: resolve polygon→cidade e alert_type→evento no banco ETL,
    monta os avisos e persiste.
    """
    execution_id = execution_id or self.request.id
    _log_safe(execution_id, "Load Iniciado", STATUS_IN_PROGRESS)

    with Timer() as timer:
        logger.info("Starting load task", task="load")

        try:
            results = analyze_output.get("results", {})
            service = LoadService(logger)
            load_result = service.process(results)

            _log_safe(
                execution_id,
                "Load Finalizado",
                STATUS_SUCCESS,
                extra={
                    "avisos_inserted": load_result.avisos_inserted,
                    "unmatched_polygons": load_result.unmatched_polygons,
                    "unmatched_events": load_result.unmatched_events,
                },
            )

            logger.info(
                "Load task completed",
                task="load",
                avisos_inserted=load_result.avisos_inserted,
                unmatched_polygons=load_result.unmatched_polygons,
                duration_seconds=timer.elapsed_seconds,
            )

            dispatch.delay(
                alerts=results,
                avisos_count=load_result.avisos_inserted,
                execution_id=execution_id,
            )

            return {
                "avisos_inserted": load_result.avisos_inserted,
                "unmatched_polygons": load_result.unmatched_polygons,
            }

        except NonRetryableException as e:
            _log_safe(execution_id, "Erro no Load", STATUS_ERROR, extra={"error": str(e)})
            logger.exception("Non-retryable error in load task", error=str(e))
            raise
        except RetryableException as e:
            _log_safe(execution_id, "Erro no Load", STATUS_ERROR, extra={"error": str(e)})
            logger.exception("Retryable error in load task", error=str(e))
            raise
        except Exception as e:
            _log_safe(execution_id, "Erro no Load", STATUS_ERROR, extra={"error": str(e)})
            raise NonRetryableException(f"Unexpected error in load: {e}") from e
```

### Task `dispatch` (encadeada após `load`)

```python
@app.task(
    bind=True,
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def dispatch(self, alerts: dict, avisos_count: int, execution_id=None):
    """
    Task 5: publica evento no Redis para o módulo de notificações.
    O payload contém apenas dados meteorológicos (sem UUIDs do modulo_usuarios).
    """
    import json
    from redis import Redis
    from domain.constants import REDIS_NOTIFICATIONS_QUEUE
    from domain.value_objects import Date

    execution_id = execution_id or self.request.id
    _log_safe(execution_id, "Dispatch Iniciado", STATUS_IN_PROGRESS)

    with Timer() as timer:
        logger.info("Starting dispatch task", task="dispatch")

        try:
            payload = {
                "execution_id": str(execution_id),
                "date": Date.get_current_date(),
                "avisos_count": avisos_count,
                "alerts": alerts,
            }

            redis = Redis.from_url(settings.REDIS_URL)
            redis.rpush(REDIS_NOTIFICATIONS_QUEUE, json.dumps(payload))

            _log_safe(execution_id, "Task Finalizada", STATUS_SUCCESS)

            logger.info(
                "Dispatch task completed",
                task="dispatch",
                queue=REDIS_NOTIFICATIONS_QUEUE,
                avisos_count=avisos_count,
                duration_seconds=timer.elapsed_seconds,
            )
            logger.info(
                "Full pipeline duration",
                duration_seconds=_pipeline_timer.elapsed_seconds,
            )

            return {"queue": REDIS_NOTIFICATIONS_QUEUE, "avisos_count": avisos_count}

        except Exception as e:
            _log_safe(execution_id, "Erro no Dispatch", STATUS_ERROR, extra={"error": str(e)})
            raise NonRetryableException(f"Unexpected error in dispatch: {e}") from e
```

### Encadear `analyze` → `load` (atualizar task `analyze` em `main.py`)

No final da task `analyze`, substituir o `return` por:

```python
# Antes (apenas salva JSON):
return {"results": results, "saved_to": output_path}

# Depois (encadeia com load):
load.delay({"results": results}, execution_id=execution_id)
return {"results": results, "saved_to": output_path}
```

---

## 7. Formato do Evento Redis (contrato com módulo de notificações)

```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2026-03-14",
  "avisos_count": 12,
  "alerts": {
    "Goiania": {
      "temperatura alta": {
        "type": "temperatura alta",
        "value": 39.5,
        "unit": "°C",
        "threshold": null,
        "difference": null,
        "seconds": 39600.0,
        "date": "2026-03-14",
        "polygon_name": "Goiania"
      },
      "umidade baixa": {
        "type": "umidade baixa",
        "value": 28.3,
        "unit": "%",
        "threshold": 60.0,
        "difference": -31.7,
        "seconds": 50400.0,
        "date": "2026-03-14",
        "polygon_name": "Goiania"
      }
    }
  }
}
```

**Observações:**
- O campo `threshold` de temperatura aparece como `null` até a resolução da task crítica no `tasks.md`
- `polygon_name` é o nome bruto do CEMPA — o módulo de notificações resolve para UUID via `modulo_usuarios`
- `execution_id` permite rastreabilidade cruzada entre ETL e módulo de notificações

---

## 8. Melhorias Identificadas no Código Existente

### 8.1 Normalização de nomes — `domain/value_objects.py`

Adicionar `CityName` como value object para encapsular a normalização:

```python
# domain/value_objects.py — adicionar ao final

import unicodedata

@dataclass(frozen=True, slots=True)
class CityName:
    """
    Encapsula nome de cidade com normalização para comparação.
    Garante que 'Goiânia', 'GOIANIA' e 'goiania' sejam tratados como iguais.
    """
    raw: str

    @property
    def normalized(self) -> str:
        nfkd = unicodedata.normalize("NFKD", self.raw)
        return nfkd.encode("ASCII", "ignore").decode("ASCII").lower().strip()

    def matches(self, other: "CityName") -> bool:
        return self.normalized == other.normalized
```

### 8.2 `domain/constants.py` — separar por contexto

```python
# Tarefas do pipeline
TASK_NAME_ETL      = "etl"
TASK_NAME_LOAD     = "load"
TASK_NAME_DISPATCH = "dispatch"

# Status de execução
STATUS_STARTED     = "STARTED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_SUCCESS     = "SUCCESS"
STATUS_ERROR       = "ERROR"

# Infraestrutura
REDIS_NOTIFICATIONS_QUEUE = "etl:notifications:ready"
```

### 8.3 `domain/exceptions.py` — adicionar exceção de catálogo vazio

```python
class CatalogEmptyException(NonRetryableException):
    """
    Lançada quando 'eventos' ou 'cidades' estão vazios no banco ETL.
    Indica que o seed não foi executado — não é um erro retryable.
    """
```

### 8.4 `infra/database/__init__.py` — exportações centralizadas

Atualmente exporta apenas `insert_application_log`. Centralizar todas as operações de banco para que os callers nunca importem os módulos internos diretamente.

---

## 9. Decisões Pendentes (bloqueia implementação parcial)

| # | Decisão | Impacto | Referência |
|---|---|---|---|
| 1 | **Threshold de temperatura** — `config.csv` local no ETL ou tabela no banco? | Bloqueia a filtragem correta antes do `load` | `tasks.md` [CRÍTICO] |
| 2 | **Mapeamento de exceções** — polígonos sem cidade (`unmatched_polygons`) devem silenciosamente ignorar ou gerar alerta de monitoramento? | Afeta observabilidade | — |
| 3 | **Idempotência do `load`** — reprocessar o mesmo dia gera avisos duplicados? Adicionar constraint `UNIQUE (id_evento, id_cidade, data_referencia)`? | Afeta consistência do banco | — |

---

## 10. Ordem de Implementação Sugerida

```
1. seed.sql                         — dados de eventos e cidades (desbloqueia tudo)
2. evento_repository.py             — leitura do catálogo
3. cidade_repository.py             — leitura do catálogo
4. aviso_repository.py              — inserção em lote
5. infra/database/__init__.py       — exportações
6. domain/value_objects.py (CityName) — normalização
7. application/load.py (LoadService) — lógica de negócio
8. domain/constants.py             — novos nomes de task e queue
9. main.py (tasks load + dispatch) — encadeamento
10. [aguarda tasks.md #1] TemperatureAnalyzer com threshold
```
