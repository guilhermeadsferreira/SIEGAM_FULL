# Análise de Comunicação — Pipeline de Notificações

> **Objetivo:** Documentar o fluxo atual de envio de notificações entre `modulo_alertas`, `modulo_usuarios` e `modulo_envios`, servindo de base para a refatoração do `modulo_envios` como novo módulo ETL.

---

## 1. Visão Geral da Arquitetura Atual

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITETURA ATUAL (estado atual)                         │
└──────────────────────────────────────────────────────────────────────────────────┘

[CEMPA]                   [modulo_alertas]           [modulo_usuarios]
tatu.cempa.ufg.br  ──►   Python (cron/script)  ──►  Quarkus / PostgreSQL
  HST*.out                  Fase 1: ETL                  porta 8002
                            Fase 2: HTTP calls           banco sigedam

                                 │
                                 │ POST /alerts/start
                                 ▼
                         [modulo_envios]             [Canais Externos]
                         Python / FastAPI  ──────►   Gmail SMTP
                              porta 8000   ──────►   Z-API (WhatsApp)
                         Redis (fila interna)
```

### Módulos e Tecnologias

| Módulo | Tecnologia | Porta | Banco |
|---|---|---|---|
| `modulo_alertas` | Python (script cron) | — | — |
| `modules/etl` | Python (Celery + FastAPI) | — | PostgreSQL 5433 (etl) |
| `modulo_usuarios` | Java / Quarkus + Panache | 8002 | PostgreSQL 5432 (sigedam) |
| `modulo_envios` | Python / FastAPI + Redis | 8000 | — (sem banco próprio) |

---

## 2. Fluxo Passo a Passo

### 2.1. Fase 1 — Coleta e Análise Meteorológica (`modulo_alertas` / `modules/etl`)

```
Execução diária (cron ou Celery Beat às 06:00 BRT)
│
├─ [PASSO 1] Controle de idempotência
│    Verifica existência de arquivo .processed para a data atual
│    Se já existir → encerra sem processar
│
├─ [PASSO 2] Limpeza e Download
│    clean_old_files() → remove arquivos antigos de tmp_files/
│    download_meteogram_file() → baixa HST{DATA} 00-MeteogramASC.out
│    de https://tatu.cempa.ufg.br/HST_Meteogramas/
│
├─ [PASSO 3] Parsing do arquivo .out
│    MeteogramParser / MeteogramTransformer
│    → filtra linhas com estado = "GO"
│    → filtra segundos entre 39.600 (08:00) e 126.000 (08:00 dia seguinte)
│    → extrai por polígono: Tmax, Tmin, Tave, TDave, Umax, Vmax, PRECmax
│
└─ [PASSO 4] Geração de alertas
     Para cada polígono (cidade):
     ├─ Temperatura Alta: Tmax(K→°C) > limiar_mensal [config.csv]
     ├─ Temperatura Baixa: Tmin(K→°C) < limiar_mensal [config.csv]
     ├─ Umidade Baixa: Magnus-Tetens(Tave, TDave) < 60%
     ├─ Vento Forte: sqrt(Umax² + Vmax²) > 11.08 m/s (≈40 km/h)
     └─ Chuva Intensa: PRECmax > 15 mm/h (⚠️ COMENTADO — inativo)
```

**Resultado:** Lista de `AvisoDTO[]` por polígono/evento.

---

### 2.2. Fase 2 — Autenticação e Persistência de Avisos (`modulo_alertas` → `modulo_usuarios`)

```
HttpClient (modulo_alertas) ──► modulo_usuarios (Quarkus)

[PASSO 5] POST /usuarios/login
  Body: { "email": "admin@admin.com", "senha": "0_=QsY86jyAE" }
  Retorna: { "token": "JWT..." }
  → Token armazenado para as próximas chamadas

[PASSO 6] GET /eventos
  Auth: Bearer JWT
  Retorna: [{ "id": "UUID", "nomeEvento": "temperatura alta", ... }]
  → Mapeamento nome_evento → id_evento

[PASSO 7] GET /cidades
  Auth: Bearer JWT
  Retorna: [{ "id": "UUID", "nome": "Goiânia", ... }]
  → Mapeamento nome_cidade → id_cidade

[PASSO 8] POST /avisos/lote
  Auth: Bearer JWT
  Body: [
    {
      "idEvento": "UUID",
      "idCidade": "UUID",
      "valor": 39.5,           // valor medido (ex: temperatura máxima)
      "valorLimite": 33.0,     // limiar configurado para o mês
      "diferenca": 6.5,        // valor - valorLimite
      "dataGeracao": "2026-03-14",
      "dataReferencia": "2026-03-14",
      "unidadeMedida": "°C",
      "horario": "08:00",
      "segundos": 39600
    },
    ...
  ]
  Retorna: 201 Created
  Persiste na tabela `avisos` do banco sigedam
```

---

### 2.3. Fase 3 — Disparo do Processamento de Envios (`modulo_alertas` → `modulo_envios`)

```
[PASSO 9] POST /alerts/start
  De: modulo_alertas (HttpClient)
  Para: modulo_envios (FastAPI)
  Body: {} (sem payload — o modulo_envios busca os avisos autonomamente)
  Retorna: 202 Accepted
  Efeito: inicia AlertService.process_all_alerts() em background task
```

---

### 2.4. Fase 4 — Busca de Avisos e Usuários (`modulo_envios` → `modulo_usuarios`)

```
AlertService.process_all_alerts():

[PASSO 10] Login no modulo_usuarios
  POST /usuarios/login
  Body: { "email": "admin@admin.com", "senha": "0_=QsY86jyAE" }
  → Token JWT obtido independentemente pelo modulo_envios

[PASSO 11] GET /avisos/today
  Auth: Bearer JWT
  Retorna: lista de avisos persistidos no passo 8
  Agrupados por cidade

[PASSO 12] Para cada aviso: GET /usuarios/preferencia/evento/{idEvento}/cidade/{idCidade}/Detalhado
  Auth: Bearer JWT
  Retorna: UsuarioDetalhadoResponseDTO[]
    {
      "id": "UUID",
      "nome": "João Silva",
      "email": "joao@email.com",
      "whatsapp": "62999999999",
      "cidadeId": "UUID",
      "cidadeNome": "Goiânia",
      "eventoId": "UUID",
      "eventoNome": "temperatura alta",
      "valor": 30.0,            // limiar personalizado do usuário (se personalizavel)
      "personalizavel": true,
      "canaisPreferidos": [
        { "id": "UUID", "nomeCanal": "Email" },
        { "id": "UUID", "nomeCanal": "Whatsapp" }
      ]
    }
```

---

### 2.5. Fase 5 — Filtragem por Preferências do Usuário (`modulo_envios` — lógica interna)

```
_filter_alerts_by_preference(usuario, aviso):

Regras aplicadas pelo modulo_envios com base em config.csv local:

├─ [TEMPERATURA]
│    Se personalizavel == true:
│      → usa limiar da preferência do usuário (campo "valor")
│      → notifica se temperatura > limiar do usuário
│    Se personalizavel == false:
│      → usa limiar padrão do config.csv por mês/polígono
│      → diferenca mínima de 5°C para alertar
│
├─ [VENTO]
│    Marca como crítico se velocidade >= 30 km/h
│    (limiar de alerta definido em 40 km/h pelo modulo_alertas)
│
├─ [UMIDADE]
│    Marca como crítico se umidade <= 30%
│    (limiar de alerta definido em 60% pelo modulo_alertas)
│
└─ [CHUVA]
     Não implementado (comentado)
```

**Problema identificado:** O `modulo_envios` relê e interpreta o `config.csv` com seus próprios critérios de criticidade, criando uma segunda camada de filtragem sobre os dados já filtrados pelo `modulo_alertas`. Isso gera acoplamento implícito via arquivo de configuração duplicado.

---

### 2.6. Fase 6 — Enfileiramento de Notificações (`modulo_envios` — Redis)

```
_formatar_alertas_por_cidade(alertas) → agrupa por cidade para o template

Para cada usuário × canal preferido:

TemplateService.generate_template():
├─ canal == "Email"     → EmailTemplateService → HTML formatado
└─ canal == "Whatsapp"  → WhatsAppTemplateService → texto simples

NotificationProducer.send_to_queue():
→ Redis RPUSH notification_queue
  Payload JSON:
  {
    "canal": { "id": "UUID", "nomeCanal": "Email" },
    "usuarios": [{ "id": "...", "email": "...", "whatsapp": "..." }],
    "conteudo": "<html>...</html>",     // ou texto plain (whatsapp)
    "alertas": [{ "tipo": "...", "valor": 39.5, "cidade": "Goiânia" }]
  }
```

---

### 2.7. Fase 7 — Consumo e Envio Real (`modulo_envios` — consumer Redis)

```
NotificationConsumer (loop blocking — thread separada):

Redis BLPOP notification_queue (timeout=0)

process_notification(payload):
│
├─ [Email]
│    EmailService.send_bulk()
│    → SMTP Gmail (smtp.gmail.com:587, STARTTLS)
│    → remetente: cempa.noreply@gmail.com
│    → conteúdo HTML
│
└─ [WhatsApp]
     WhatsAppService.send_bulk()
     → POST https://api.z-api.io/instances/{INSTANCE}/token/{TOKEN}/send-text
     → autenticação via Client-Token header
     → conteúdo texto simples

Após envio (sucesso ou falha):
ExternalIntegrationService.create_envio()
→ GET /status → busca ID do status "Sucesso" ou "Falha"
→ POST /envios (modulo_usuarios)
  Body: {
    "idCanal": "UUID",
    "idAviso": "UUID",
    "idUsuarioDestinatario": "UUID",
    "idStatus": "UUID"
  }
```

---

### 2.8. Fase 8 — Persistência do Registro de Envio (`modulo_usuarios`)

```
POST /envios → persiste na tabela `envios`:
  (id, id_canal, id_aviso, id_usuario_destinatario, id_status)

Serve como histórico de rastreabilidade:
  quem recebeu, qual canal, qual aviso, qual foi o resultado
```

---

## 3. Diagrama de Sequência Completo

```
CEMPA          modulo_alertas      modulo_usuarios     modulo_envios    Redis    Gmail/Z-API
  │                  │                    │                  │             │           │
  │ HST*.out         │                    │                  │             │           │
  │─────────────────►│                    │                  │             │           │
  │                  │ POST /login        │                  │             │           │
  │                  │───────────────────►│                  │             │           │
  │                  │ JWT token          │                  │             │           │
  │                  │◄───────────────────│                  │             │           │
  │                  │ GET /eventos       │                  │             │           │
  │                  │───────────────────►│                  │             │           │
  │                  │ GET /cidades       │                  │             │           │
  │                  │───────────────────►│                  │             │           │
  │                  │ POST /avisos/lote  │                  │             │           │
  │                  │───────────────────►│                  │             │           │
  │                  │ 201 Created        │                  │             │           │
  │                  │◄───────────────────│                  │             │           │
  │                  │ POST /alerts/start │                  │             │           │
  │                  │──────────────────────────────────────►│             │           │
  │                  │ 202 Accepted       │                  │             │           │
  │                  │◄──────────────────────────────────────│             │           │
  │                  │                    │ POST /login       │             │           │
  │                  │                    │◄─────────────────│             │           │
  │                  │                    │ JWT token        │             │           │
  │                  │                    │─────────────────►│             │           │
  │                  │                    │ GET /avisos/today │             │           │
  │                  │                    │◄─────────────────│             │           │
  │                  │                    │ avisos[]         │             │           │
  │                  │                    │─────────────────►│             │           │
  │                  │                    │ GET /pref/evento/│cidade/Det.  │           │
  │                  │                    │◄─────────────────│  (N vezes)  │           │
  │                  │                    │ usuarios[]       │             │           │
  │                  │                    │─────────────────►│             │           │
  │                  │                    │                  │ RPUSH       │           │
  │                  │                    │                  │────────────►│           │
  │                  │                    │                  │ BLPOP       │           │
  │                  │                    │                  │◄────────────│           │
  │                  │                    │                  │ send email  │           │
  │                  │                    │                  │────────────────────────►│
  │                  │                    │ POST /envios     │             │           │
  │                  │                    │◄─────────────────│             │           │
  │                  │                    │ 201 Created      │             │           │
  │                  │                    │─────────────────►│             │           │
```

---

## 4. Entidades e Persistência

### Banco `sigedam` (modulo_usuarios — PostgreSQL)

```
cidades
  id UUID PK, nome VARCHAR

canais
  id UUID PK, nome_canal VARCHAR, data_inclusao TIMESTAMP

eventos
  id UUID PK, nome_evento VARCHAR, personalizavel BOOLEAN, horario TIMESTAMP

usuarios
  id UUID PK, nome, email, whatsapp, senha, login_token
  nivel_acesso: ADMIN | CLIENTE

preferencias
  id UUID PK
  id_usuario FK → usuarios
  id_evento FK → eventos
  id_cidade FK → cidades
  valor FLOAT           ← limiar personalizado do usuário
  personalizavel BOOL
  id_canal FK → canais

avisos
  id UUID PK
  id_evento FK → eventos
  id_cidade FK → cidades
  valor FLOAT           ← valor medido (ex: 39.5°C)
  valor_limite FLOAT    ← limiar padrão (ex: 33.0°C)
  diferenca FLOAT       ← valor - valor_limite
  unidade_medida VARCHAR
  data_geracao DATE
  data_referencia DATE
  horario TIME
  segundos INT

possiveis_status
  id UUID PK, nome_status VARCHAR, id_canal FK → canais

envios
  id UUID PK
  id_canal FK → canais
  id_aviso FK → avisos
  id_usuario_destinatario FK → usuarios
  id_status FK → possiveis_status
```

### Banco `etl` (modules/etl — PostgreSQL separado, porta 5433)

```
application_logs
  id UUID PK
  task VARCHAR(100)          ← nome da task Celery
  execution_id UUID          ← ID único por execução
  message VARCHAR(255)
  status VARCHAR(20)         ← STARTED | IN_PROGRESS | SUCCESS | ERROR
  extra JSONB
  created_at TIMESTAMPTZ
```

---

## 5. Contratos de API (DTOs)

### `AvisoDTO` — `modulo_alertas` → `modulo_usuarios`
```json
{
  "idEvento": "UUID",
  "idCidade": "UUID",
  "valor": 39.5,
  "valorLimite": 33.0,
  "diferenca": 6.5,
  "dataGeracao": "2026-03-14",
  "dataReferencia": "2026-03-14",
  "unidadeMedida": "°C",
  "horario": "08:00",
  "segundos": 39600
}
```

### `UsuarioDetalhadoResponseDTO` — `modulo_usuarios` → `modulo_envios`
```json
{
  "id": "UUID",
  "nome": "João Silva",
  "email": "joao@email.com",
  "whatsapp": "62999999999",
  "cidadeId": "UUID",
  "cidadeNome": "Goiânia",
  "eventoId": "UUID",
  "eventoNome": "temperatura alta",
  "valor": 30.0,
  "personalizavel": true,
  "canaisPreferidos": [
    { "id": "UUID", "nomeCanal": "Email" },
    { "id": "UUID", "nomeCanal": "Whatsapp" }
  ]
}
```

### `EnvioRequestDTO` — `modulo_envios` → `modulo_usuarios`
```json
{
  "idCanal": "UUID",
  "idAviso": "UUID",
  "idUsuarioDestinatario": "UUID",
  "idStatus": "UUID"
}
```

---

## 6. Regras de Negócio

### 6.1 Geração de Alertas (módulo ETL)

| Evento | Variável | Condição | Observação |
|---|---|---|---|
| `temperatura alta` | `Tmax` (K→°C) | `Tmax > limiar_mensal_csv` | Limiar varia por mês e polígono |
| `temperatura baixa` | `Tmin` (K→°C) | `Tmin < limiar_mensal_csv` | Limiar varia por mês e polígono |
| `umidade baixa` | `Tave + TDave` → Magnus-Tetens | Umidade relativa < 60% | Formulação psicométrica |
| `vento forte` | `sqrt(Umax² + Vmax²)` | Velocidade > 11.08 m/s (~40 km/h) | Composição vetorial |
| `chuva intensa` | `PRECmax` | > 15 mm/h | **Inativo — comentado** |

### 6.2 Filtragem por Preferência (modulo_envios)

- Se `preferencia.personalizavel == true`: o usuário define seu próprio limiar — notificação só é enviada se o valor medido supera o limiar do usuário
- Se `preferencia.personalizavel == false`: usa limiar padrão do `config.csv` com diferença mínima de 5°C
- Criticidade de vento: marcado como "crítico" se velocidade ≥ 30 km/h
- Criticidade de umidade: marcado como "crítico" se umidade ≤ 30%

### 6.3 Canais de Notificação

- Cada usuário tem `canaisPreferidos[]` (Email e/ou WhatsApp)
- Uma notificação separada é enfileirada para cada canal
- Templates distintos por canal (HTML para email, texto plano para WhatsApp)

### 6.4 Rastreabilidade

- Todo envio (bem-sucedido ou falho) gera um registro em `envios` no `modulo_usuarios`
- Status possíveis: `Sucesso` e `Falha` (por canal)

---

## 7. Problemas Identificados

### 7.1 Dois Pipelines Paralelos em Conflito
O `modules/etl` (Celery) e o `modulo_alertas` (script cron) executam o mesmo trabalho de coleta e análise. O ETL ainda **não faz chamadas HTTP** — apenas salva em JSON local — enquanto o `modulo_alertas` é o que efetivamente dispara o fluxo de notificações. São dois sistemas rodando em paralelo com código duplicado.

### 7.2 `config.csv` Duplicado
O arquivo de limiares mensais de temperatura existe em dois lugares:
- `backend/modulo_alertas/config.csv`
- `backend/modulo_envios/src/config.csv`

Ambos com o mesmo conteúdo. Qualquer atualização de limiares precisa ser feita nos dois lugares, sendo uma fonte de inconsistência.

### 7.3 Credenciais Admin Hardcoded
O `modulo_envios` autentica no `modulo_usuarios` com `admin@admin.com` / `0_=QsY86jyAE` para ter acesso aos endpoints de admin. Credenciais hardcoded no `.env` e sem rotação.

### 7.4 Dupla Filtragem de Alertas
1. O `modulo_alertas` já filtra/gera apenas avisos que ultrapassam limiares
2. O `modulo_envios` **refiltra** com seus próprios critérios de criticidade usando o mesmo `config.csv`

Isso cria uma lógica de negócio fragmentada entre dois módulos.

### 7.5 N+1 de Chamadas HTTP para Busca de Usuários
Para cada aviso retornado por `/avisos/today`, o `modulo_envios` faz uma chamada individual para `/usuarios/preferencia/evento/{id}/cidade/{id}/Detalhado`. Se houver 10 avisos, são 10 chamadas síncronas antes de enfileirar as notificações.

### 7.6 Sem Banco Próprio no `modulo_envios`
O `modulo_envios` não persiste nenhum estado local. O Redis é apenas fila in-memory. Não há como reprocessar notificações falhas ou auditar tentativas sem o `modulo_usuarios`.

### 7.7 `modulo_envios` sem Isolamento Real
A chamada `POST /alerts/start` inicia processamento em background sem nenhum mecanismo de:
- Controle de reprocessamento (pode ser chamado múltiplas vezes)
- Rastreamento de execução em andamento
- Retry controlado de falhas de envio

### 7.8 Alerta de Chuva Inativo
O tipo de evento `chuva intensa` existe no banco (`eventos`) mas o código de geração está comentado. O evento fica órfão no sistema.

---

## 8. Dependências de Infraestrutura

```
┌─────────────────────────────────────────────────────────────┐
│                    INFRAESTRUTURA ATUAL                      │
├──────────────┬──────────────────────────────────────────────┤
│ Serviço      │ Detalhes                                      │
├──────────────┼──────────────────────────────────────────────┤
│ PostgreSQL   │ sigedam: porta 5432, banco sigedam           │
│              │ etl: porta 5433, banco etl                   │
├──────────────┼──────────────────────────────────────────────┤
│ Redis        │ sigedam-redis: porta 6379 (modulo_envios)    │
│              │ etl-redis: porta 6380 (modules/etl)          │
├──────────────┼──────────────────────────────────────────────┤
│ Gmail SMTP   │ smtp.gmail.com:587, App Password             │
├──────────────┼──────────────────────────────────────────────┤
│ Z-API        │ api.z-api.io (WhatsApp Business)             │
├──────────────┼──────────────────────────────────────────────┤
│ CEMPA        │ tatu.cempa.ufg.br/HST_Meteogramas/           │
└──────────────┴──────────────────────────────────────────────┘
```

---

## 9. Estado Atual vs. Estado Desejado (Pós-Refatoração)

```
ESTADO ATUAL (legado)                   ESTADO DESEJADO (pós-refatoração)
─────────────────────────────────────   ──────────────────────────────────────
modulo_alertas (cron python)            modules/etl (Celery)
  └─ download + parse + HTTP calls        └─ download + transform + analyze
                                            └─ [novo] HTTP calls para usuarios
                                               [novo] HTTP calls para envios

modulo_envios (FastAPI + Redis)         [novo módulo] modules/notifications
  └─ sem banco                            └─ com banco próprio
  └─ config.csv duplicado                 └─ recebe config de modulo_usuarios
  └─ filtragem duplicada                  └─ filtragem única e centralizada
  └─ sem idempotência                     └─ idempotência via execution_id
```

---

## 10. Perguntas em Aberto para a Refatoração

1. **O `modulo_envios` deve virar um módulo Celery (como o ETL) ou manter FastAPI?**
   - FastAPI para receber trigger externo + Celery para processamento assíncrono?
   - Ou pipeline puramente Celery integrado ao `modules/etl`?

2. **O `config.csv` deve ser centralizado onde?**
   - Banco de dados do `modulo_usuarios` (já tem a tabela `preferencias` e `eventos`)?
   - Arquivo único versionado compartilhado?

3. **A dupla filtragem de criticidade deve ser unificada?**
   - A lógica de "crítico" (vento ≥ 30 km/h, umidade ≤ 30%) deve ir para o ETL ou para o módulo de notificações?

4. **O `modulo_envios` deve ter banco próprio?**
   - Para logs de execução e retry de falhas?
   - Separado do `modulo_usuarios` (que já tem a tabela `envios`)?

5. **A autenticação admin deve ser repensada?**
   - Service account com token de longa duração?
   - Comunicação interna sem autenticação (mesma rede privada)?
