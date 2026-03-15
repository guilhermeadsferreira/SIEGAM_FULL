# Status dos Módulos — Resumo Executivo

> Visão consolidada do estado atual dos módulos ETL e Notifications. Para o report semanal ao time de produtos, use [`documentacao/progress.md`](../documentacao/progress.md).

---

## Módulos

| Módulo | Papel | Status |
|--------|-------|--------|
| **ETL** | Processa dados meteorológicos, gera avisos e publica na fila de notificações | Operacional |
| **Notifications** | Consome a fila, filtra por preferência do usuário e envia (e-mail, WhatsApp) | Implementado, em validação |

---

## O que está pronto

- **Pipeline completo:** Download → Transform → Load → Dispatch → Consumer → Envio
- **Filtragem de temperatura:** Limiares mensais por município aplicados no ETL (≥ 5°C de diferença)
- **Refatoração do módulo de envios:** Novo módulo de notificações com acesso direto ao banco, templates, retry e registro de envios

---

## Pendências antes do cutover

| Prioridade | Item |
|------------|------|
| Alta | Graceful shutdown e health check no consumer |
| Média | Comunicar ativação do alerta de chuva (antes desativado no legado) |
| Média | Decisões: polígonos sem cidade, idempotência ao reprocessar |

---

## Documentação

- **Report para stakeholders:** [`documentacao/progress.md`](../documentacao/progress.md) — o que fizemos, por que fizemos
- **Backlog técnico:** [`documentacao/tasks.md`](../documentacao/tasks.md) — tarefas, decisões pendentes
- **Fluxo ponta a ponta:** [`modules/FLUXO_COMPLETO.md`](FLUXO_COMPLETO.md)
- **Fichas dos módulos:** [`etl/MODULE.md`](etl/MODULE.md), [`notifications/MODULE.md`](notifications/MODULE.md)
