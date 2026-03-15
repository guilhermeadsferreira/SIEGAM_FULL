# Fluxo Completo — Do Dado Meteorológico à Notificação do Usuário

> Documento de referência que descreve, passo a passo, toda a cadeia de processamento desde a origem dos dados no CEMPA/UFG até o momento em que o usuário recebe um alerta no celular ou e-mail.
>
> **Estado:** descreve o sistema após a refatoração (`modules/etl` + `modules/notifications`). Para entender as decisões que motivaram a refatoração, consulte `modules/notifications/MODULE.md`.

---

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                        MÓDULO ETL                               │
│                                                                 │
│  CEMPA/UFG ──► Download ──► Transform ──► Analyze ──► Load      │
│                                                      │          │
│                                                      ▼          │
│                                                  [avisos]       │
│                                                  no banco       │
│                                                      │          │
│                                                      ▼          │
│                                                   Dispatch      │
│                                                      │          │
└──────────────────────────────────────────────────────┼──────────┘
                                                       │
                                        Redis: etl:notifications:ready
                                                       │
                                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                   MÓDULO DE NOTIFICAÇÕES                         │
│                                                                  │
│  Consumer ──► Resolver ──► Filtrar por ──► Renderizar ──► Enviar │
│  (Redis)      usuários      preferência    templates    e-mail / │
│                  │              │              │        WhatsApp  │
│                  │              │              │             │    │
│                  └──────────────┴──────────────┘             │    │
│                                                              ▼    │
│                                                     Registrar     │
│                                                     envio no DB   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Parte 1 — ETL: Do arquivo bruto ao alerta

### Passo 1: Download do Meteograma

**Quando:** Diariamente às 06:00 (America/Sao_Paulo), via Celery Beat.

**O que acontece:**
- O ETL faz HTTP GET para a URL do CEMPA/UFG
- Arquivo esperado: `HST{YYYYMMDD}00-MeteogramASC.out`
- Valida tamanho mínimo (100 bytes)
- Salva o arquivo em `tmp/meteograms/`

**Resiliência:** Se falhar (rede, timeout), faz retry automático com backoff exponencial (máx. 3 tentativas).

**Saída:** Arquivo ASC local no disco.

---

### Passo 2: Transformação (ASC → JSON)

**O que acontece:**
- Lê o arquivo ASC (formato tabular proprietário do CEMPA)
- Filtra por **janela de tempo**: 11h a 35h (39.600s a 126.000s)
- Filtra por **estado**: apenas polígonos de Goiás
- Extrai colunas: `Tmax`, `Tmin`, `Tave`, `TDave`, `Umax`, `Vmax`, `PRECmax`
- Agrupa dados por polígono e por timestamp

**Saída:** JSON estruturado por polígono.

```json
{
  "Goiania": {
    "39600.0": { "Tmax": 310.5, "Tmin": 295.2, "Umax": -3.1, "Vmax": 5.2 },
    "43200.0": { "..." }
  },
  "Anapolis": { "..." }
}
```

---

### Passo 3: Análise (JSON → Alertas)

Quatro analisadores independentes processam cada polígono.

#### 3a. Temperatura

Para cada polígono, encontra:
- **Temperatura máxima** (maior `Tmax` em Kelvin → Celsius)
- **Temperatura mínima** (menor `Tmin` em Kelvin → Celsius)

**Validação:** descarta valores fora de 200–350 K.

**Conversão:** `Celsius = Kelvin - 273.15`

> ⚠️ **Decisão pendente:** O `TemperatureAnalyzer` atualmente **sempre gera alerta** para todo polígono com dados válidos, sem verificar threshold mensal. A filtragem por limiar mensal (config.csv) ainda não foi implementada no ETL. Ver `documentacao/tasks.md` → "TemperatureAnalyzer não aplica threshold".

**Saída por polígono:** Até 2 alertas (`temperatura alta` e `temperatura baixa`).

#### 3b. Umidade Relativa

Para cada polígono, calcula umidade relativa via fórmula de Magnus:
- Usa `Tave` (temperatura média) e `TDave` (ponto de orvalho médio)
- Converte Kelvin → Celsius antes do cálculo
- Clamp resultado entre 0% e 100%

**Gera alerta se:** menor umidade do dia < **60%**.

**Saída:** No máximo 1 alerta (`umidade baixa`).

#### 3c. Vento

Para cada polígono, calcula velocidade do vento:
- Fórmula: `√(Umax² + Vmax²) × 3.6` (componentes → km/h)
- Descarta se componente > 100 ou resultado > 200 km/h

**Gera alerta se:** maior velocidade do dia > **12 km/h**.

**Saída:** No máximo 1 alerta (`vento`).

#### 3d. Chuva

Para cada polígono, encontra a maior taxa de precipitação (`PRECmax`).

**Gera alerta se:** maior precipitação > **15 mm/h**.

**Saída:** No máximo 1 alerta (`chuva`).

> **Nota:** O alerta de chuva estava inativo no sistema legado (`backend/modulo_alertas`). No ETL refatorado, está ativo. Usuários inscritos em eventos de chuva passarão a receber notificações que antes não recebiam. Confirmar com stakeholders antes do cutover.

#### Resumo da análise

Cada polígono pode gerar **até 5 alertas** por dia:

| Tipo | Condição para gerar | Valor registrado |
|------|---------------------|-----------------|
| Temperatura alta | Sempre (threshold pendente) | Máxima em °C |
| Temperatura baixa | Sempre (threshold pendente) | Mínima em °C |
| Umidade baixa | Mínima < 60% | Menor umidade em % |
| Vento | Máxima > 12 km/h | Maior velocidade em km/h |
| Chuva | Máxima > 15 mm/h | Maior precipitação em mm/h |

Com ~249 polígonos de Goiás, o sistema pode gerar até ~1.245 alertas por dia.

---

### Passo 4: Carga (Alertas → Avisos no Banco)

**O que acontece:**
1. Carrega catálogos do banco: cidades e tipos de evento
2. Para cada alerta:
   - **Mapeia polígono → cidade**: normaliza nomes (NFKD, ASCII, lowercase) e compara com as cidades cadastradas; como fallback, usa o `display_name` do `config.csv`
   - **Mapeia tipo de alerta → evento**: ex: `"umidade baixa"` → UUID do evento no banco
3. Monta registro de aviso com: `id_evento`, `id_cidade`, `valor`, `valor_limite`, `diferença`, `unidade_medida`, `data_referencia`, `horario`
4. Insere todos os avisos em batch na tabela `avisos` e retorna os UUIDs gerados

**Polígonos sem match:** Registrados como `unmatched` no log, não geram aviso.

**Saída:** Avisos persistidos no PostgreSQL com seus UUIDs, prontos para rastreabilidade.

---

### Passo 5: Dispatch (Avisos → Fila Redis)

**O que acontece:**
- Publica payload na fila `etl:notifications:ready` com os UUIDs gerados no Load:

```json
{
  "execution_id": "uuid-da-execução",
  "date": "2026-03-14",
  "avisos_count": 87,
  "alerts": [
    {
      "aviso_id": "uuid-do-aviso",
      "id_cidade": "uuid-da-cidade",
      "id_evento": "uuid-do-evento",
      "nome_cidade": "Goiânia",
      "nome_evento": "temperatura alta",
      "valor": 38.2,
      "unidade_medida": "°C",
      "horario": "14:00:00",
      "data_referencia": "2026-03-14"
    }
  ]
}
```

---

## Parte 2 — Notificações: Do alerta ao celular do usuário

### Passo 6: Consumo da Fila

**Como acontece:**
- O `NotificationConsumer` entra em loop bloqueante (`BLPOP`) na fila `etl:notifications:ready`
- Ao receber uma mensagem, desserializa o payload e inicia o pipeline de notificações
- Mensagens que falham repetidamente vão para `etl:notifications:dead-letter`

**Entrada:** `ExecutionPayload` com lista de `AlertPayload`.

---

### Passo 7: Resolver Destinatários

**O que acontece:**
1. Extrai todos os pares `(id_evento, id_cidade)` do payload
2. Faz **uma única query em batch** no banco para buscar todos os usuários inscritos nessas combinações, incluindo:
   - Dados do usuário: nome, email, whatsapp
   - Preferência: `personalizavel` (bool), `valor` (threshold pessoal), `canais_preferidos`
3. Agrupa resultado: `{ usuario_id: { usuario, alertas } }`

**Saída:** Dicionário de usuários → alertas que lhes são relevantes.

---

### Passo 8: Filtrar por Preferência do Usuário

Para cada par (usuário, alerta), aplica a lógica:

#### 8a. Temperatura (alta ou baixa)

```
Preferência personalizável?
  │
  ├─ NÃO → ✅ ENVIA (crítico por padrão)
  │
  └─ SIM → Valor de preferência definido?
           │
           ├─ NÃO → ✅ ENVIA
           │
           └─ SIM → Temperatura baixa: valor < preferência? → ✅
                     Temperatura alta:  valor > preferência? → ✅
                     Caso contrário → ❌ NÃO ENVIA
```

> ⚠️ **Atenção:** Esta lógica assume que o ETL já aplicou o threshold mensal de temperatura antes de publicar o aviso. Enquanto o ETL não implementar esse filtro, todos os alertas de temperatura passarão e todos os usuários com `personalizavel=false` receberão notificações. Ver `documentacao/tasks.md`.

#### 8b. Vento e Umidade

```
Valor de preferência definido?
  │
  ├─ NÃO → O alerta é crítico? (vento ≥ 30 km/h ou umidade ≤ 30%)
  │         ├─ SIM → ✅ ENVIA
  │         └─ NÃO → ❌ NÃO ENVIA
  │
  └─ SIM → Preferência personalizável?
           ├─ NÃO → O alerta é crítico? → SIM ✅ / NÃO ❌
           └─ SIM → Umidade: valor < preferência? → ✅
                    Vento:   valor > preferência? → ✅
```

#### 8c. Chuva

Sempre enviada (crítica por definição), independente de preferência.

#### Tabela de criticidade

| Evento | Condição para ser "crítico" |
|--------|----------------------------|
| Chuva | Sempre crítico |
| Temperatura alta | Sempre crítico (sujeito ao threshold mensal pendente no ETL) |
| Temperatura baixa | Sempre crítico (sujeito ao threshold mensal pendente no ETL) |
| Vento | Valor ≥ 30 km/h |
| Umidade baixa | Valor ≤ 30% |

---

### Passo 9: Formatar Alertas por Cidade

**O que acontece:**
- Os alertas filtrados são agrupados por `id_cidade`
- Para cada alerta, o template calcula o **período**: horário ± 1h (ex: "13:00 às 15:00")
- UF "GO" é adicionada (hardcoded — expansão para outros estados é trabalho futuro)

---

### Passo 10: Renderizar Template por Canal

Para cada canal preferido do usuário (email, WhatsApp), gera o conteúdo:

#### E-mail (HTML)

- Header com "Resumo de Avisos Meteorológicos"
- Blocos por cidade com alertas individuais
- Cada alerta tem cor baseada na severidade:
  - Vermelho (`#e74c3c`): chuva forte, temperatura, umidade ≤ 30%, vento ≥ 30 km/h
  - Laranja (`#f39c12`): chuva moderada, umidade 30–60%, vento < 30 km/h
- Footer com link para gerenciamento de preferências

#### WhatsApp (texto)

- Emojis por tipo de alerta (❄️ 🔥 💧 💨 🌧️)
- Formatação bold com asteriscos
- Blocos por cidade
- Footer com link para gerenciamento

#### Níveis de severidade por evento

| Umidade | Nível |
|---------|-------|
| 30–60% | Crítico para a saúde humana |
| 21–30% | Estado de Atenção |
| 12–21% | Estado de Alerta |
| < 12% | Estado de Emergência |

| Vento | Nível |
|-------|-------|
| 12–20 km/h | Brisa fraca |
| 20–30 km/h | Brisa moderada |
| 30–40 km/h | Ventania |
| 40–50 km/h | Forte ventania |
| > 50 km/h | Vento forte |

| Chuva | Nível |
|-------|-------|
| 15–25 mm/h | Moderada |
| > 25 mm/h | Forte |

---

### Passo 11: Envio Efetivo

#### E-mail (SMTP)

1. Conecta ao Gmail SMTP (`smtp.gmail.com:587`, TLS)
2. Autentica com app password
3. Envia para o destinatário
4. Em caso de falha: registra status "Falha" (não propaga exceção, não perde as demais notificações)

#### WhatsApp (Z-API)

1. Normaliza o telefone (adiciona DDI `55` se ausente)
2. Faz `POST` para `api.z-api.io` com o texto
3. Em caso de falha: registra status "Falha" e segue para o próximo usuário

---

### Passo 12: Registrar Resultado do Envio

**Após envio (sucesso ou falha):**
- Para cada aviso × usuário, verifica idempotência: `envio_exists(id_canal, aviso_id, id_usuario)`
- Se já existe registro, ignora (previne duplicatas em caso de reprocessamento)
- Se não existe, insere na tabela `envios`:
  - `id_canal`: UUID do canal (e-mail ou WhatsApp)
  - `id_aviso`: UUID do aviso gerado pelo ETL
  - `id_usuario_destinatario`: UUID do usuário
  - `id_status`: UUID do status ("Sucesso" ou "Falha")

---

## Decisões e Pendências

| # | Questão | Status | Ref |
|---|---------|--------|-----|
| 1 | Threshold de temperatura: mover para o ETL ou reimplementar no Notifications? | **Pendente** | `tasks.md` |
| 2 | Polígonos sem match no Load: falha silenciosa ou erro explícito acima de X%? | **Pendente** | `tasks.md` |
| 3 | Idempotência na tabela `avisos` (`UNIQUE` constraint)? | **Pendente** | `tasks.md` |
| 4 | Graceful shutdown e health check no consumer | **Pendente** | `tasks.md` |
| 5 | Comunicar ativação do alerta de chuva com stakeholders | **Pendente** | `tasks.md` |
| 6 | UF "GO" hardcoded — expansão para outros estados? | **Backlog** | `dispatcher.py:113` |

---

## Integrações por Módulo

### ETL (`modules/etl`)

| Sistema | Direção | Finalidade |
|---------|---------|-----------|
| CEMPA/UFG | Entrada | Download do meteograma ASC |
| PostgreSQL | Saída | Persistência de avisos, leitura de cidades e eventos |
| Redis | Saída | Publicação em `etl:notifications:ready`; broker Celery |

### Notifications (`modules/notifications`)

| Sistema | Direção | Finalidade |
|---------|---------|-----------|
| Redis | Entrada | Consumo de `etl:notifications:ready` |
| PostgreSQL | Entrada/Saída | Consulta de usuários/preferências; registro de envios |
| Gmail SMTP | Saída | Envio de e-mails |
| Z-API | Saída | Envio de mensagens WhatsApp |
