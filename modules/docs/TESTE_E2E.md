# Teste E2E Controlado — ETL → Notificações WhatsApp

> **Objetivo**: Executar o pipeline completo localmente:
> CEMPA/UFG → ETL → Redis → Notifications → WhatsApp
>
> **Escopo**: WhatsApp apenas. Email ignorado neste teste.
> **Ambiente**: Local via Docker (stack raiz `modules/docker-compose.yml`)
> **Atualizado**: 2026-03-28

---

## Estado atual da infraestrutura

Já resolvido em sessões anteriores:

| Item | Status |
|------|--------|
| `modules/docker-compose.yml` — stack unificada | ✅ Criado |
| `modules/init-db/` — schema + seed de cidades/eventos | ✅ Movido para raiz |
| `modules/.env.example` | ✅ Criado |
| `modules/Makefile` | ✅ Criado |
| `etl/Dockerfile` — `uv sync` duplicado removido | ✅ Corrigido |
| `notifications/Dockerfile` — migrado para `uv` | ✅ Corrigido |
| Rede `sigedam-net` compartilhada entre os dois módulos | ✅ Configurado |
| Schema + cidades + eventos aplicados automaticamente no boot | ✅ Via `init-db/` |

---

## O que ainda falta para o teste

```
[ ] 1. Criar modules/.env com credenciais Z-API
[ ] 2. Criar init-db/seed_e2e.sql com usuários de teste
[ ] 3. Subir a stack e aplicar seed_e2e.sql
[ ] 4. Disparar o ETL manualmente
[ ] 5. Verificar WhatsApp recebido + banco
```

---

## Passo 1 — Criar `.env`

```bash
cd modules
cp .env.example .env
```

Preencher no `.env`:

```dotenv
WHATSAPP_INSTANCE=<sua-instancia>
WHATSAPP_TOKEN=<seu-token>
WHATSAPP_CLIENT_TOKEN=<seu-client-token>
```

O restante já tem valores padrão no `.env.example`.

---

## Passo 2 — Criar `init-db/seed_e2e.sql`

> Cidades e eventos **não precisam** estar aqui — o `seed.sql` já os insere no boot.
> Este seed trata apenas dos dados de teste: canais, usuários e preferências.
> Usa subqueries para referenciar os UUIDs de eventos/cidades pelo nome
> (já que foram gerados com `gen_random_uuid()` no `seed.sql`).

```sql
-- init-db/seed_e2e.sql
-- Dados de teste para E2E controlado.
-- Executar após a stack estar no ar (schema.sql + seed.sql já aplicados).
-- Idempotente: ON CONFLICT DO NOTHING em todas as inserções.

-- =============================================================================
-- 1. Canais
-- =============================================================================
INSERT INTO canais (id, nome_canal, data_inclusao) VALUES
  ('00000000-0000-0000-0000-000000000001', 'whatsapp', CURRENT_DATE),
  ('00000000-0000-0000-0000-000000000002', 'email',    CURRENT_DATE)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 2. Status possíveis por canal
-- =============================================================================
INSERT INTO possiveis_status (id, nome_status, id_canal) VALUES
  ('00000000-0000-0000-0001-000000000001', 'Sucesso', '00000000-0000-0000-0000-000000000001'),
  ('00000000-0000-0000-0001-000000000002', 'Falha',   '00000000-0000-0000-0000-000000000001'),
  ('00000000-0000-0000-0001-000000000003', 'Sucesso', '00000000-0000-0000-0000-000000000002'),
  ('00000000-0000-0000-0001-000000000004', 'Falha',   '00000000-0000-0000-0000-000000000002')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 3. Usuários de teste (dois números reais para receber WhatsApp)
-- =============================================================================
INSERT INTO usuarios (id, nome, email, whatsapp, data_criacao, data_ultima_edicao, senha, nivel_acesso)
VALUES
  (
    '00000000-0000-0000-0004-000000000001',
    'Teste E2E - Usuario 1',
    'teste1@e2e.local',
    '62996401335',
    NOW(), CURRENT_DATE, 'hash-nao-usado', 'admin'
  ),
  (
    '00000000-0000-0000-0004-000000000002',
    'Teste E2E - Usuario 2',
    'teste2@e2e.local',
    '62985804130',
    NOW(), CURRENT_DATE, 'hash-nao-usado', 'admin'
  )
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 4. Vincular usuários ao canal WhatsApp
-- =============================================================================
INSERT INTO usuario_canais_preferidos (id_usuario, id_canal)
VALUES
  ('00000000-0000-0000-0004-000000000001', '00000000-0000-0000-0000-000000000001'),
  ('00000000-0000-0000-0004-000000000002', '00000000-0000-0000-0000-000000000001')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 5. Preferências: ambos os usuários para todos os tipos de alerta em Goiânia
-- Usa subquery para buscar os UUIDs reais de eventos e cidades pelo nome.
-- =============================================================================
INSERT INTO preferencias (id, id_usuario, id_evento, id_cidade, data_criacao, data_ultima_edicao, personalizavel)
SELECT
  gen_random_uuid(),
  u.id,
  e.id,
  c.id,
  CURRENT_DATE,
  CURRENT_DATE,
  false
FROM
  (VALUES
    ('00000000-0000-0000-0004-000000000001'),
    ('00000000-0000-0000-0004-000000000002')
  ) AS u(id)
  CROSS JOIN eventos e
  CROSS JOIN cidades c
WHERE
  c.nome = 'Goiânia'
  AND e.nome_evento IN ('temperatura alta', 'temperatura baixa', 'umidade baixa', 'vento', 'chuva')
ON CONFLICT DO NOTHING;
```

Salvar em `modules/init-db/seed_e2e.sql`.

---

## Passo 3 — Subir a stack e aplicar o seed

```bash
cd modules

# Subir tudo (db + redis + etl worker + notifications consumer)
make up

# Aguardar containers ficarem healthy
make ps

# Aplicar seed de teste (canais, usuários, preferências)
make seed
```

O `make seed` roda:
```
psql postgresql://cempa:cempa@localhost:5432/sigedam -f init-db/seed_e2e.sql
```

> **Atenção**: `schema.sql` e `seed.sql` (cidades + eventos) já foram aplicados
> automaticamente pelo PostgreSQL no boot. O `seed_e2e.sql` só adiciona o que falta.

---

## Passo 4 — Disparar o ETL

```bash
make run-once
```

Isso executa dentro do container:
```
uv run python run_once.py → download_file.delay()
```

Acompanhar logs em tempo real:

```bash
make logs-etl
```

Sequência esperada:

```
[download]  STARTED  → baixando HST20260328_MeteogramASC.out
[download]  SUCCESS  → arquivo salvo
[transform] STARTED  → parseando binário CEMPA
[transform] SUCCESS  → JSON gerado
[analyze]   STARTED  → detectando alertas
[analyze]   SUCCESS  → N alertas encontrados
[load]      STARTED  → mapeando polígonos → cidades
[load]      SUCCESS  → N avisos inseridos
[dispatch]  STARTED  → publicando no Redis
[dispatch]  SUCCESS  → payload em etl:notifications:ready
```

Verificar se a mensagem chegou na fila:

```bash
docker compose exec redis redis-cli LLEN etl:notifications:ready
# Deve retornar: 1
```

---

## Passo 5 — Verificar notificações

O consumer já está rodando desde o `make up`. Assim que o ETL publicar no Redis,
o consumer processa automaticamente.

```bash
make logs-notifications
```

Sequência esperada:

```
[consumer]   mensagem recebida — execution_id=... avisos_count=N
[resolver]   2 usuários encontrados
[filter]     usuário 'Teste E2E - Usuario 1': N alertas
[filter]     usuário 'Teste E2E - Usuario 2': N alertas
[dispatcher] enviando whatsapp → 62996401335
[dispatcher] enviando whatsapp → 62985804130
[consumer]   mensagem processada com sucesso
```

---

## Passo 6 — Checklist de sucesso

```
[ ] WhatsApp recebido no número 62996401335
[ ] WhatsApp recebido no número 62985804130
[ ] Tabela envios: 2 registros, canal=whatsapp, status=Sucesso
[ ] Tabela application_logs: todos os steps com status=SUCCESS
[ ] Fila etl:notifications:ready: LLEN = 0 (consumida)
[ ] Fila etl:notifications:dead-letter: LLEN = 0 (sem erros)
```

Queries de verificação:

```sql
-- Envios registrados
SELECT u.nome, c.nome_canal, ps.nome_status
FROM envios en
JOIN usuarios u          ON u.id  = en.id_usuario_destinatario
JOIN canais c            ON c.id  = en.id_canal
JOIN possiveis_status ps ON ps.id = en.id_status
ORDER BY en.id DESC;

-- Logs ETL
SELECT task, status, message, created_at
FROM application_logs
ORDER BY created_at DESC
LIMIT 20;

-- Avisos gerados
SELECT id_cidade, id_evento, valor, unidade_medida, data_referencia
FROM avisos
ORDER BY data_geracao DESC
LIMIT 10;
```

---

## Troubleshooting

### ETL falha no `load` — polígono não encontrado

O nome do polígono no arquivo `.out` não bate com nenhuma cidade do banco.
Ver o JSON gerado após o transform:

```bash
docker compose exec celery_worker \
  cat tmp/meteograms/HST*MeteogramASC.json | python3 -m json.tool | grep -i goiania
```

Conferir os nomes normalizados no banco:

```sql
SELECT nome FROM cidades ORDER BY nome;
```

### Notifications não encontra usuários

```sql
SELECT p.id_usuario, e.nome_evento, c.nome
FROM preferencias p
JOIN eventos e ON e.id = p.id_evento
JOIN cidades c ON c.id = p.id_cidade;
```

Se vazio: seed_e2e.sql não foi aplicado ou o nome da cidade na query não bateu.

### Z-API retorna erro

- Confirmar instância Z-API conectada (WhatsApp Web ativo na instância)
- Verificar WHATSAPP_INSTANCE, WHATSAPP_TOKEN, WHATSAPP_CLIENT_TOKEN no `.env`
- Números devem estar sem `+` e sem `-` (ex: `62996401335`)

### Repetir o teste (limpar estado)

```bash
# Limpar Redis
docker compose exec redis redis-cli FLUSHDB

# Limpar registros do banco (mantém seed)
docker compose exec db psql -U cempa -d sigedam -c \
  "DELETE FROM envios; DELETE FROM avisos; DELETE FROM application_logs;"

# Reset completo (apaga volumes)
make clean && make up && make seed
```
