# Fluxo E2E — ETL → Redis → Notifications → WhatsApp

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         make run-once                                       │
│                    (você executa este comando)                               │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  CONTAINER: celery_worker                                                   │
│                                                                             │
│  run_once.py → download_file.delay()                                        │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  TASK 1: download_file                                               │   │
│  │  GET https://cempa.ufg.br/.../HST{DATA}_MeteogramASC.out             │   │
│  │  → salva em tmp/meteograms/HST{DATA}_MeteogramASC.out                │   │
│  │  → on_success: transform_file.delay(filepath)                        │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
│  ┌─────────────────────────────▼────────────────────────────────────────┐   │
│  │  TASK 2: transform_file                                              │   │
│  │  Parseia binário ASC → extrai polígonos + valores meteorológicos     │   │
│  │  → salva em tmp/meteograms/HST{DATA}_MeteogramASC.json               │   │
│  │  → on_success: analyze_data.delay(filepath)                          │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
│  ┌─────────────────────────────▼────────────────────────────────────────┐   │
│  │  TASK 3: analyze_data                                                │   │
│  │  Lê JSON → aplica thresholds por tipo de evento                      │   │
│  │  (temperatura > X, umidade < Y, vento > Z, chuva...)                 │   │
│  │  → identifica quais polígonos disparam alertas                       │   │
│  │  → on_success: load_data.delay(alerts)                               │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
│  ┌─────────────────────────────▼────────────────────────────────────────┐   │
│  │  TASK 4: load_data                                                   │   │
│  │  Para cada alerta:                                                   │   │
│  │    nome_poligono → busca cidade em PostgreSQL (tabela cidades)        │   │
│  │    → INSERT INTO avisos (id_cidade, id_evento, valor, ...)            │   │
│  │  → on_success: dispatch_notifications.delay(execution_id)            │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
│  ┌─────────────────────────────▼────────────────────────────────────────┐   │
│  │  TASK 5: dispatch_notifications                                      │   │
│  │  Monta payload JSON com todos os avisos do execution_id              │   │
│  │  → RPUSH etl:notifications:ready <payload>  (Redis)                  │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
└────────────────────────────────┼────────────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  REDIS                  │
                    │  key: etl:notifications │
                    │       :ready            │
                    │  LLEN → 1               │
                    └────────────┬────────────┘
                                 │
                    BLPOP (blocking pop)
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│  CONTAINER: notifications                                                   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 1: consume                                                     │   │
│  │  Lê payload do Redis → extrai execution_id + lista de avisos         │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
│  ┌─────────────────────────────▼────────────────────────────────────────┐   │
│  │  STEP 2: resolve recipients                                          │   │
│  │  SELECT usuarios com preferencias para as cidades/eventos alertados  │   │
│  │  → encontra: Teste E2E - Usuario 1, Teste E2E - Usuario 2            │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
│  ┌─────────────────────────────▼────────────────────────────────────────┐   │
│  │  STEP 3: filter                                                      │   │
│  │  Para cada usuário: quais alertas batem com suas preferências?       │   │
│  │  (eventos + cidades configurados em preferencias)                    │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
│  ┌─────────────────────────────▼────────────────────────────────────────┐   │
│  │  STEP 4: render                                                      │   │
│  │  Monta mensagem de texto WhatsApp com os alertas filtrados           │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
│  ┌─────────────────────────────▼────────────────────────────────────────┐   │
│  │  STEP 5: dispatch                                                    │   │
│  │  POST https://api.z-api.io/instances/{INSTANCE}/token/{TOKEN}        │   │
│  │       /send-text                                                     │   │
│  │  body: { phone: "62996401335", message: "..." }                      │   │
│  │  body: { phone: "62985804130", message: "..." }                      │   │
│  │  → INSERT INTO envios (id_usuario, id_canal, id_status, ...)         │   │
│  └─────────────────────────────┬────────────────────────────────────────┘   │
│                                │                                            │
└────────────────────────────────┼────────────────────────────────────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   Z-API                   │
                    │   (WhatsApp gateway)      │
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │  WhatsApp recebido em:    │
                    │  62996401335              │
                    │  62985804130              │
                    └───────────────────────────┘
```

## Pontos de falha a monitorar

| Etapa | O que pode falhar |
|-------|------------------|
| `download` | URL do CEMPA fora do ar ou arquivo do dia não publicado ainda |
| `load` | Nome do polígono não bate com `cidades.nome` no banco |
| `resolve` | `seed_e2e.sql` não foi aplicado → nenhum usuário encontrado |
| `dispatch` (Z-API) | Credenciais erradas ou instância desconectada |
