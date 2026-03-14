# Tasks — Refatoração módulo_envios

> Registro de tarefas, pontos críticos e decisões pendentes identificadas durante a análise e refatoração.

---

## Em aberto

### [CRÍTICO] `TemperatureAnalyzer` não aplica threshold

**Arquivo:** `modules/etl/application/analyzer/temperature.py`

**Problema:**
O `TemperatureAnalyzer` retorna alertas de temperatura para **todo polígono analisado**, sem verificar se a temperatura ultrapassou um limiar. Diferente do `HumidityAnalyzer` e do `WindAnalyzer`, que filtram pelo threshold antes de emitir o alerta, o analyzer de temperatura sempre emite `temperatura alta` e `temperatura baixa` com `threshold=None` e `difference=None`.

```python
# Como está hoje (sem filtro):
alerts["temperatura alta"] = Alert(
    type="temperatura alta",
    value=max_temp_c,
    unit="°C",
    threshold=None,   # ← sem threshold aplicado
    difference=None,  # ← sem diferença calculada
    ...
)

# Como deveria ser (com filtro, igual humidity/wind):
if max_temp_c > threshold_para_este_poligono_e_mes:
    alerts["temperatura alta"] = Alert(...)
```

**Impacto:**
Quando o ETL assumir a responsabilidade de persistir avisos (`Task 4 — load`), ele enviaria registros de temperatura para **todas as cidades todos os dias**, mesmo quando a temperatura está dentro do normal. Isso corromperia a tabela `avisos` e geraria notificações incorretas para os usuários.

**O que precisa ser decidido antes de resolver:**
- [ ] O limiar de temperatura continua no `config.csv` (limiares mensais por polígono) ou migra para o banco do `modulo_usuarios`?
- [ ] Se ficar no CSV: o `TemperatureAnalyzer` recebe os limiares via injeção (dict `{mes: {poligono: limiar}}`) ou lê o CSV diretamente?
- [ ] Se migrar para o banco: criar novo endpoint em `modulo_usuarios` ou usar a tabela `preferencias` existente para limiares padrão?

**Contexto adicional:**
- Os limiares de temperatura hoje estão em `backend/modulo_alertas/config.csv` e `backend/modulo_envios/src/config.csv` (duplicados)
- O `modulo_envios` também usa esses limiares para refiltragem — ao centralizar no ETL, o `modulo_envios` deixa de precisar do `config.csv`
- Referência: `analise_modulo_envios.md` → seção 7.2 (config.csv duplicado) e seção 7.4 (dupla filtragem)

---

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

## Concluídas

_(nenhuma ainda)_
