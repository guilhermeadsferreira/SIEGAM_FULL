# Tasks — Refatoração módulo_envios

> Registro de tarefas, pontos críticos e decisões pendentes identificadas durante a análise e refatoração.

**Relatório para stakeholders:** O narrativo de *o que fizemos* e *por que fizemos* (linguagem de produto) está em [`progress.md`](progress.md). Use esse documento para reports semanais ao time de produtos.

---

## Responsabilidades do ETL

| # | Responsabilidade | Status |
|---|------------------|--------|
| 1 | Buscar eventos no banco | Concluída |
| 2 | Buscar cidades no banco | Concluída |
| 3 | Persistir avisos gerados | Concluída |
| 4 | Publicar evento no Redis para o módulo de notificações | Concluída |
| 5 | Aplicar threshold de temperatura antes de emitir alertas | Concluída |

---

## Em aberto

### Polígonos sem correspondência de cidade no `load`

**Arquivo:** `modules/etl/application/load.py` (a ser criado — ver `etl_plan.md`)

**Problema:**
Quando o `LoadService` tentar resolver `polygon_name → UUID da cidade`, alguns polígonos do CEMPA podem não ter correspondência na tabela `cidades` do banco ETL (grafia diferente, município novo, erro no seed). A decisão de como tratar esses casos ainda não foi tomada.

**Opções:**
- [ ] Ignorar silenciosamente (comportamento atual previsto no plano — apenas log `warning`)
- [ ] Lançar exceção `NonRetryableException` se a taxa de não-match superar um limiar (ex: > 10% dos polígonos sem match → algo está errado com o seed)
- [ ] Publicar métrica/alerta de monitoramento separado para polígonos sem match

**O que precisa ser decidido:**
- [ ] Qual é o comportamento aceitável: falha silenciosa ou erro explícito?
- [ ] Existe um limiar de tolerância para polígonos sem match?

**Ref:** `etl_plan.md` — seção `application/load.py`, método `_resolve_cidade`

---

### Idempotência do `load` — reprocessamento do mesmo dia

**Arquivo:** `modules/etl/init-db/schema.sql` e `modules/etl/infra/database/aviso_repository.py` (a ser criado)

**Problema:**
Se a task `load` for reexecutada no mesmo dia (retry do Celery, reprocessamento manual ou falha parcial), ela vai inserir avisos duplicados na tabela `avisos`. Atualmente o schema não tem nenhuma constraint que impeça isso.

**Solução proposta:**
Adicionar `UNIQUE (id_evento, id_cidade, data_referencia)` na tabela `avisos` e usar `INSERT ... ON CONFLICT DO NOTHING` no repositório.

**O que precisa ser decidido:**
- [ ] Confirmar que um aviso por evento+cidade+dia é suficiente (não há cenário de múltiplos avisos do mesmo tipo no mesmo dia)
- [ ] Definir se o `ON CONFLICT` deve ser `DO NOTHING` (ignora silenciosamente) ou `DO UPDATE` (atualiza o valor se o arquivo foi reprocessado com dado mais recente)

**Ref:** `etl_plan.md` — seção `infra/database/aviso_repository.py`; `init-db/schema.sql` linha 76 (TODO inline)

---

### [MÉDIO] Consumer sem graceful shutdown e health check

**Arquivo:** `modules/notifications/main.py`, `modules/notifications/infra/redis/queue_consumer.py`

**Problema:**
O consumer que lê a fila Redis não tem:
- **Health check:** processo pode morrer silenciosamente sem que a orquestração (Docker, Kubernetes) detecte
- **Graceful shutdown:** ao receber SIGTERM (deploy, restart de container), pode abandonar uma mensagem em processamento a meio, perdendo-a

**Identificado em:** FLUXO_COMPLETO.md — Problema #7 ("Consumer frágil"), mas não registrado como task acionável.

**Impacto:** Em qualquer restart do container, uma mensagem ativa pode ser descartada sem ser processada, sem nenhum registro de falha.

**O que precisa ser implementado:**
- [ ] Capturar `SIGTERM` no `main.py` e sinalizar ao consumer para parar de aceitar novas mensagens, aguardando o processamento atual terminar
- [ ] Expor endpoint `/health` (ou heartbeat via log) detectável pelo healthcheck do Docker

---

### [NOTA] Chuva ativa pela primeira vez — mudança de comportamento em relação ao legado

**Contexto:**
No módulo legado (`backend/modulo_alertas`), o alerta de chuva estava **comentado** no código e, portanto, **nunca gerava avisos nem notificações**. No novo ETL, o `RainAnalyzer` está **ativo** com threshold de 15 mm/h.

**Impacto para os usuários:**
Ao ativar o novo pipeline, usuários inscritos em eventos de chuva passarão a receber notificações que antes nunca chegavam. Isso pode surpreender stakeholders e usuários finais.

**O que precisa ser feito antes do cutover:**
- [ ] Confirmar com os stakeholders que a ativação do alerta de chuva é intencional e planejada
- [ ] Verificar se há usuários inscritos em eventos de chuva no banco e avaliar impacto de comunicação

---

### [BAIXO] MODULE.md do Notifications com contrato de payload e checklist desatualizados

**Arquivo:** `modules/notifications/MODULE.md`

**Problemas identificados:**

1. **Contrato JSON incorreto:** O schema de entrada mostra campos em camelCase (`idCidade`, `idEvento`, `id`), mas o ETL publica em snake_case (`id_cidade`, `id_evento`, `aviso_id`). Qualquer desenvolvedor que integrar baseado no MODULE.md usará os campos errados.

2. **Plano de Migração obsoleto:** Todos os checkboxes aparecem como `[ ]` (pendente), mas as Fases 1–4 estão implementadas. Apenas a Fase 5 (validação e cutover) está em andamento.

3. **Integração incorreta:** A seção "Integrações" lista "API de Usuários | HTTP (saída)" para consulta de preferências, mas o módulo acessa o banco diretamente via `usuario_repository.py` — sem chamadas HTTP ao `modulo_usuarios`.

**Impacto:** O MODULE.md é o primeiro documento que um desenvolvedor lê. Ter informações incorretas aumenta o risco de bugs de integração e onboarding incorreto.

---

## Concluídas

### TemperatureAnalyzer — aplicação de threshold de temperatura

**Arquivo:** `modules/etl/application/analyzer/temperature.py`

**O que foi feito:** O analisador de temperatura passou a aplicar limiares mensais por município (via `config.csv`), emitindo alertas apenas quando a diferença em relação ao esperado for relevante (≥ 5°C). Usa `TemperatureConfig` para carregar os limiares e `should_emit_max_alert` / `should_emit_min_alert` para decidir se emite o alerta.

**Por que:** Evitar envio de alertas de temperatura para todas as cidades todos os dias, mesmo quando dentro do normal. Centralizar a filtragem no ETL elimina duplicação de critérios e permite remover o `config.csv` do módulo de envios.

**Narrativo para stakeholders:** Ver [`progress.md`](progress.md) — 14/03/2026, "Implementação do módulo de notificações e ajustes no ETL".

---

### Refatoração do módulo de envios → módulo de notificações

**Escopo:** `modules/notifications/` (novo módulo)

**O que foi feito:** Novo módulo de notificações com acesso direto ao banco, filtragem por preferência do usuário, templates para e-mail e WhatsApp, envio com retry, registro de envios com idempotência, consumer da fila Redis com graceful shutdown e dead-letter queue.

**Por que:** O módulo de envios legado apresentava débitos técnicos (perda silenciosa de mensagens, dependência de trigger manual, falta de visibilidade). A refatoração aplica práticas consolidadas no ETL e elimina pontos de falha.

**Narrativo para stakeholders:** Ver [`progress.md`](progress.md) — 14/03/2026, "Implementação do módulo de notificações e ajustes no ETL" e "Planejamento da refatoração do módulo de envios".
