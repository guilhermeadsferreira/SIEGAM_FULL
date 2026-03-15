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

#### Documentação: Responsabilidades do ETL

**O que fizemos:** Criamos uma seção em `tasks.md` que lista as cinco responsabilidades do módulo ETL e o status de cada uma (concluída ou pendente).

**Por que fizemos:** Centralizar a visão do que o ETL deve fazer e o que ainda falta implementar, facilitando o acompanhamento e a comunicação com stakeholders.

#### Documentação: Impacto da task pendente de temperatura no módulo de envios

**O que fizemos:** Adicionamos em `tasks.md`, na descrição da task pendente de threshold de temperatura, uma nota explícita sobre o impacto direto no módulo de envios enquanto a task não for concluída.

**Por que fizemos:** Deixar registrado que a remoção do arquivo de configuração local do módulo de envios depende da resolução desta task — sem esse contexto, uma refatoração futura poderia remover a filtragem do módulo de envios prematuramente e causar envio incorreto de notificações para os usuários.

#### Documentação de escopo dos módulos

**O que fizemos:** Criamos uma ficha técnica (`MODULE.md`) para o módulo ETL com papel, responsabilidades, fluxo de execução, regras de negócio e integrações. Também adicionamos uma regra de projeto que exige a atualização dessa ficha sempre que houver mudança de escopo ou responsabilidade em qualquer módulo.

**Por que fizemos:** Até agora não havia documentação clara do que cada módulo faz e quais são seus limites. Com a ficha e a regra, toda alteração que mude o papel de um módulo será automaticamente documentada, evitando que o conhecimento fique apenas no código ou na cabeça dos desenvolvedores.

#### Planejamento da refatoração do módulo de envios

**O que fizemos:** Realizamos uma análise completa do módulo de envios atual e documentamos o planejamento de refatoração no novo módulo de notificações (`modules/notifications/MODULE.md`). O documento cobre: problemas que afetam disponibilidade, escalabilidade e resiliência; responsabilidades do módulo; fluxo de operação; regras de negócio; arquitetura proposta com separação em camadas; e um plano de migração em 5 fases.

**Por que fizemos:** O módulo de envios atual apresenta fragilidades que impactam a confiabilidade das notificações enviadas aos usuários — desde perda silenciosa de mensagens até falta de visibilidade operacional. Documentar o plano antes de executar permite validar a abordagem com a equipe, evitar retrabalho e garantir que a migração ocorra de forma controlada, sem interrupção do serviço.

#### Documentação do fluxo completo (ETL → Notificação)

**O que fizemos:** Criamos um documento detalhado (`modules/notifications/FLUXO_COMPLETO.md`) que descreve, passo a passo, toda a cadeia desde o download do arquivo meteorológico até o momento em que o usuário recebe a notificação. O documento identificou problemas estruturais no fluxo, incluindo uma desconexão entre os módulos e filtragem duplicada com critérios diferentes.

**Por que fizemos:** O fluxo atravessa dois módulos com regras de negócio distintas, e não havia documentação que mostrasse a cadeia completa. Sem essa visão de ponta a ponta, não é possível tomar decisões informadas sobre o que melhorar — como a questão dos thresholds de temperatura, que hoje estão no lugar errado da cadeia.

#### Implementação do módulo de notificações e ajustes no ETL

**O que fizemos:** Implementamos o novo módulo de notificações (`modules/notifications`) conforme o plano de refatoração, e realizamos os ajustes necessários no ETL para suportá-lo:

- **ETL:** O dispatch passou a incluir os IDs dos avisos inseridos no payload publicado na fila Redis, permitindo que o módulo de notificações registre corretamente cada envio. O analisador de temperatura passou a aplicar limiares mensais por município (via `config.csv`), emitindo alertas apenas quando a diferença em relação ao esperado for relevante (≥ 5°C).
- **Módulo de notificações:** Estrutura completa com acesso direto ao banco de dados para buscar usuários e preferências em lote, filtragem por preferência do usuário, templates compartilhados para e-mail e WhatsApp, envio com retry e backoff, registro de envios com verificação de idempotência, e consumer da fila com graceful shutdown e dead-letter queue.

**Por que fizemos:** O módulo de envios atual apresenta débitos técnicos que comprometem disponibilidade, escalabilidade e resiliência. A refatoração aplica as mesmas práticas consolidadas no módulo de ETL (configuração centralizada, logging estruturado, hierarquia de exceções, acesso direto ao banco) e elimina pontos de falha como a dependência de trigger manual e a perda silenciosa de mensagens.

#### Revisão de cobertura: o que ficou para trás na refatoração

**O que fizemos:** Comparamos os módulos legados (`backend/modulo_alertas` e `backend/modulo_envios`) com os novos (`modules/etl` e `modules/notifications`) para identificar regras de negócio que possam ter ficado de fora ou desalinhadas. Atualizamos o `tasks.md` com os gaps encontrados e corrigimos documentações desatualizadas.

Os principais achados foram:
- O módulo de notificações foi escrito assumindo que o ETL já filtra temperatura por limiar mensal — mas essa filtragem ainda não foi implementada, criando risco de envio em massa incorreto ao ligar o pipeline
- O consumer de notificações ainda não tem mecanismo de desligamento seguro nem de verificação de saúde
- A funcionalidade de alerta de chuva, que estava desativada no sistema antigo, agora está ativa — o que precisa ser comunicado antes de virar ao vivo
- O documento de fluxo completo foi movido para o nível de módulos e reescrito para refletir o estado atual (em vez do estado legado e do "proposto")
- O `MODULE.md` do módulo de notificações tinha o contrato de integração incorreto (campos de dados com nomes errados) e o checklist de fases como se nada tivesse sido feito

**Por que fizemos:** Com dois sistemas rodando em paralelo (legado e refatorado), o risco de deixar regras de negócio para trás sem perceber é alto. A revisão explícita — olhando código a código — é a única forma de garantir que nada crítico se perca na transição.

---

## 15/03/2026

### Tópico do dia: Roteiro de teste integrado focado em WhatsApp

**O que fizemos**

Criamos um roteiro de teste integrado para validar a cadeia completa de notificações, desde o processamento de dados meteorológicos no ETL até o envio de mensagens para usuários via WhatsApp, usando apenas o novo módulo de notificações. O material foi registrado dentro do módulo de notificações, com instruções claras de preparação de dados, configuração de ambiente e critérios de sucesso.

**Por que fizemos**

Precisamos de um caminho previsível para testar a integração entre os módulos antes de qualquer migração definitiva, garantindo que avisos gerados pelo processamento sejam entregues corretamente a usuários reais em um canal específico. Ao focar inicialmente em WhatsApp e documentar o fluxo de teste, facilitamos a validação com o time de produto e reduzimos o risco de surpresas quando o novo módulo assumir o papel do sistema legado.

---

## Próximos passos (backlog)

| Prioridade | Item | Status |
|------------|------|--------|
| Alta | Graceful shutdown e health check no consumer de notificações | Pendente |
| Média | Comunicar ativação do alerta de chuva com stakeholders antes do cutover | Pendente |
| Média | Definir comportamento quando uma região meteorológica não corresponde a nenhuma cidade | Pendente decisão |
| Média | Avaliar idempotência ao reprocessar o mesmo dia (UNIQUE na tabela avisos) | Pendente decisão |
| Baixa | Remover UF "GO" hardcoded — preparar expansão para outros estados | Backlog |

---

## Como usar este documento

- **Novo dia:** Se não existir seção para a data atual, criar `## DD/MM/YYYY` com "Tópico do dia"
- **Linguagem:** Produto e negócio; evitar jargão técnico
- **Foco:** O que mudou e por que — especialmente em refatorações
