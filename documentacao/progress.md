# Progresso — Relatório para Stakeholders

> Documento de acompanhamento das evoluções do projeto. Atualizado sempre que houver alterações significativas. Linguagem voltada a relatórios para stakeholders.

---

## Estrutura

- **Por dia:** Cada entrada usa o formato `DD/MM/YYYY`
- **Tópico do dia:** Se não existir entrada para o dia, criar um novo tópico
- **O que fizemos:** Descrição em linguagem de produto
- **Por que fizemos:** Motivação, especialmente em refatorações

---

## 14/03/2026

### Tópico do dia: Pipeline meteorológico completo e autônomo

**O que fizemos**

O sistema de processamento de dados meteorológicos passou a operar de forma **independente**, sem depender de outros módulos durante a execução. Foram adicionadas duas novas etapas no fluxo:

- **Carga (Load):** Conecta os alertas meteorológicos às cidades e tipos de evento cadastrados, e grava os avisos no banco
- **Distribuição (Dispatch):** Envia os avisos para a fila de notificações, permitindo que o módulo de alertas envie mensagens aos usuários (WhatsApp, e-mail, etc.)

Também foi criado um catálogo de dados de referência (5 tipos de evento e 249 municípios de Goiás) que o sistema utiliza para funcionar, e o registro de andamento de cada etapa nos logs foi ampliado.

**Por que fizemos**

1. **Resiliência:** O pipeline não depende mais de chamadas a outros serviços durante a execução, reduzindo pontos de falha.
2. **Responsabilidade única:** O ETL concentra a lógica de processamento e persistência de avisos, simplificando a arquitetura e a manutenção.
3. **Preparação para notificações:** Com a etapa de distribuição, os avisos chegam à fila que o módulo de notificações consome.
4. **Transparência:** Logs e rastreabilidade facilitam o suporte e a investigação de problemas em produção.

---

## Próximos passos (backlog)

| Prioridade | Item | Status |
|------------|------|--------|
| Crítica | Definir regra de limiar para alertas de temperatura (evitar avisos em excesso) | Pendente decisão |
| Média | Definir comportamento quando uma região meteorológica não corresponde a nenhuma cidade | Pendente decisão |
| Média | Avaliar idempotência ao reprocessar o mesmo dia | Pendente decisão |

---

## Como usar este documento

- **Novo dia:** Se não existir seção para a data atual, criar `## DD/MM/YYYY` com "Tópico do dia"
- **Linguagem:** Produto e negócio; evitar jargão técnico
- **Foco:** O que mudou e por que — especialmente em refatorações
