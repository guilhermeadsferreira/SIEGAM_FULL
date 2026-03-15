# Notifications — Definição do Módulo

## Papel

Consumir avisos meteorológicos publicados pelo módulo de ETL, resolver destinatários com base em preferências de usuários, renderizar conteúdo por canal (e-mail, WhatsApp) e despachar as notificações, registrando o resultado de cada envio.

---

## Motivação da Refatoração

O módulo atual (`backend/modulo_envios`) funciona em produção, mas acumula débitos técnicos que comprometem **disponibilidade**, **escalabilidade** e **resiliência** do sistema. A refatoração migra o código para `modules/notifications` aplicando as mesmas práticas já consolidadas no módulo de ETL.

### Problemas que afetam a disponibilidade

| Problema | Impacto | Onde ocorre |
|----------|---------|-------------|
| **Consumer síncrono com `asyncio.run()` em loop** | Cada mensagem cria e destrói um event loop; overhead alto e risco de deadlock | `notification_consumer.py:88` |
| **Sem health check no consumer** | Processo pode morrer silenciosamente sem ser detectado | Consumer roda como `__main__` isolado |
| **`print` como único mecanismo de log** | Sem visibilidade operacional; perda de contexto em incidentes | Todo o módulo (~50 ocorrências) |
| **Credenciais hardcoded como fallback** | Se `.env` falhar, senha padrão é exposta em texto claro | `external_integration_service.py:11` |
| **`print` de credenciais em stdout** | Senha do e-mail aparece no log ao inicializar `EmailService` | `email_service.py:14` |
| **Sem retry em falhas de envio** | Falha transitória de SMTP ou Z-API perde a notificação permanentemente | `email_service.py`, `whatsapp_service.py` |
| **Sem dead-letter queue** | Mensagens que falham repetidamente são perdidas | `notification_consumer.py` |

### Problemas que afetam a escalabilidade

| Problema | Impacto | Onde ocorre |
|----------|---------|-------------|
| **Requisições HTTP sequenciais por usuário** | N alertas × M cidades × K usuários = milhares de requests síncronos | `alert_service.py:242-248` |
| **Uma conexão SMTP por envio** | Abre/fecha conexão TLS a cada `send()`, sem pool | `email_service.py:57` |
| **Dependência do `pandas` para ler CSV** | Biblioteca pesada para operação trivial (tabela de limiares) | `config_parser.py` |
| **Consumer single-threaded** | Um único processo consome a fila; gargalo em picos | `notification_consumer.py:85` |
| **Nomes de filas hardcoded** | `"notification_queue"` fixo no código ignora `config.py` | `notification_producer.py:7`, `notification_consumer.py:13` |

### Problemas que afetam a resiliência

| Problema | Impacto | Onde ocorre |
|----------|---------|-------------|
| **Sem hierarquia de exceções** | `except Exception` genérico; não diferencia erros retryable de fatais | Todo o módulo |
| **Falha silenciosa nos services de envio** | `EmailService.send()` retorna `False` sem propagar erro | `email_service.py:63` |
| **`traceback.print_exc()` em vez de logging** | Stack trace vai para stdout sem metadata estruturada | `alert_service.py:321` |
| **Sem circuit breaker para APIs externas** | Se `modulo_usuarios` ficar fora, consumer trava indefinidamente | `external_integration_service.py` |
| **Token refresh sem mutex** | Requisições concorrentes podem causar login duplicado | `external_integration_service.py:59-65` |
| **Sem idempotência** | Reprocessar mensagem da fila pode gerar envios duplicados | `notification_consumer.py` |

### Problemas de qualidade de código

| Problema | Impacto |
|----------|---------|
| **God class `AlertService`** | 324 linhas com filtragem, formatação, agrupamento e orquestração misturados |
| **Código duplicado** | `_format_data_pt_br` idêntico em `EmailTemplateService` e `WhatsAppTemplateService` |
| **Lógica de criticidade duplicada** | Níveis de vento, umidade e chuva repetidos nos templates e no `AlertService` |
| **`load_dotenv()` chamado em 4 arquivos** | Configuração descentralizada e imprevisível |
| **Sem testes** | Zero testes automatizados; sem cobertura |
| **Sem `requirements.txt`** | Dependências não rastreadas |
| **UF "GO" hardcoded** | Impossível expandir para outros estados |
| **Sem `__init__.py`** | Imports relativos frágeis |

---

## Responsabilidades

- **Consumir** avisos da fila Redis `etl:notifications:ready` publicada pelo ETL
- **Resolver** destinatários consultando preferências de usuários por cidade/evento
- **Filtrar** alertas por preferência individual (valor, personalizável, limiares de temperatura)
- **Renderizar** conteúdo por canal (HTML para e-mail, texto para WhatsApp)
- **Despachar** notificações via SMTP (e-mail) e Z-API (WhatsApp)
- **Registrar** resultado de cada envio (sucesso/falha) no banco de dados
- **Expor** API HTTP para disparo manual e testes de template

---

## Fluxo

```
Consume → Resolve → Filter → Render → Dispatch → Record
```

| Etapa | Entrada | Saída |
|-------|---------|-------|
| **Consume** | Mensagem da fila `etl:notifications:ready` | Payload com avisos e metadata |
| **Resolve** | IDs de cidade + evento | Lista de usuários com preferências |
| **Filter** | Alertas + preferências do usuário | Alertas relevantes por usuário |
| **Render** | Alertas filtrados + canal | Conteúdo formatado (HTML ou texto) |
| **Dispatch** | Conteúdo + destinatários | Resultado de envio por destinatário |
| **Record** | Resultado do envio | Registro na tabela `envios` |

---

## Regras de Negócio

### Resolução de destinatários

- Para cada aviso (cidade + evento), consultar usuários inscritos na preferência correspondente
- Respeitar canais preferidos do usuário (`canaisPreferidos`)
- Usuários sem canal configurado não recebem notificação

### Filtragem por preferência

| Cenário | Comportamento |
|---------|---------------|
| Temperatura (alta/baixa) | Comparar valor do alerta com limiar mensal do município; enviar se diferença ≥ 5°C |
| Preferência `personalizavel=false` | Enviar apenas se alerta for crítico (vento ≥ 30, umidade ≤ 30, chuva sempre) |
| Preferência `personalizavel=true` | Enviar se valor do alerta ultrapassa o valor configurado pelo usuário |
| Sem preferência definida | Enviar se alerta for crítico |

### Criticidade

| Evento | Condição crítica |
|--------|-----------------|
| Chuva | Sempre crítico |
| Temperatura alta | Sempre crítico (se ultrapassar limiar) |
| Temperatura baixa | Sempre crítico (se ultrapassar limiar) |
| Vento | Crítico se valor ≥ 30 km/h |
| Umidade baixa | Crítico se valor ≤ 30% |

### Templates

- **E-mail:** HTML com blocos por cidade, cores por severidade, link de descadastro
- **WhatsApp:** Texto formatado com emojis, blocos por cidade, link de gerenciamento

### Registro de envios

- Após despacho bem-sucedido: registrar com status "Sucesso"
- Após falha no despacho: registrar com status "Falha"
- Cada registro contém: `idCanal`, `idAviso`, `idUsuarioDestinatario`, `idStatus`

---

## Arquitetura Proposta

### Estrutura de diretórios

```
modules/notifications/
├── .env.example
├── .gitignore
├── .python-version
├── MODULE.md
├── README.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── Makefile
├── main.py                        # Entry point — consumer da fila
├── settings.py                    # Pydantic Settings centralizado
│
├── domain/
│   ├── __init__.py
│   ├── constants.py               # Nomes de fila, status, task names
│   ├── entities.py                # Alert, Notification, UserPreference
│   ├── exceptions.py              # Hierarquia: Retryable vs NonRetryable
│   ├── value_objects.py           # Channel, AlertSeverity, PhoneNumber
│   └── protocols.py               # Protocol para Sender, TemplateRenderer
│
├── application/
│   ├── __init__.py
│   ├── consumer.py                # Consume fila Redis e orquestra pipeline
│   ├── resolver.py                # Resolve destinatários por cidade/evento
│   ├── filter.py                  # Filtra alertas por preferência do usuário
│   ├── dispatcher.py              # Orquestra renderização + envio + registro
│   └── templates/
│       ├── __init__.py
│       ├── base.py                # Lógica compartilhada (_format_data_pt_br, severidade)
│       ├── email_renderer.py      # Gera HTML para e-mail
│       └── whatsapp_renderer.py   # Gera texto para WhatsApp
│
├── infra/
│   ├── __init__.py
│   ├── logger/
│   │   ├── __init__.py
│   │   └── json_logger.py         # Logging estruturado JSON
│   ├── http/
│   │   ├── __init__.py
│   │   └── api_client.py          # HTTP client com retry, timeout, auth
│   ├── senders/
│   │   ├── __init__.py
│   │   ├── email_sender.py        # SMTP com connection pool
│   │   └── whatsapp_sender.py     # Z-API com retry
│   ├── database/
│   │   ├── __init__.py
│   │   ├── postgres.py            # Context manager get_connection()
│   │   └── envio_repository.py    # Persistência de envios
│   └── redis/
│       ├── __init__.py
│       └── queue_consumer.py      # Abstração de leitura da fila
│
└── scripts/
    └── verify_db.py
```

### Camadas

| Camada | Responsabilidade | Regra |
|--------|------------------|-------|
| **Domain** | Entidades, value objects, exceções, protocols | Não importa nada de infra ou application |
| **Application** | Casos de uso e orquestração | Importa domain; usa infra via injeção |
| **Infrastructure** | Banco, HTTP, SMTP, Redis, logger | Implementa protocols do domain |

### Comparação com o módulo atual

| Aspecto | `modulo_envios` (atual) | `modules/notifications` (proposto) |
|---------|------------------------|-------------------------------------|
| Configuração | `load_dotenv()` em 4 arquivos | Pydantic Settings centralizado |
| Logging | `print()` (~50 ocorrências) | Logger JSON estruturado |
| Exceções | `except Exception` genérico | Hierarquia Retryable / NonRetryable |
| God class | `AlertService` (324 linhas) | Separado em `resolver`, `filter`, `dispatcher` |
| Templates | Código duplicado entre canais | Base class com lógica compartilhada |
| SMTP | Conexão por envio | Connection pool reutilizável |
| Consumer | `asyncio.run()` em loop `while True` | Consumer estruturado com graceful shutdown |
| Testes | Zero | Cobertura em domain e application |
| Retry | Nenhum | Retry com backoff em envios e HTTP |
| Dead-letter | Não existe | Fila de mensagens falhadas |
| Idempotência | Não existe | Check de envio duplicado antes de registrar |

---

## Padrões e Práticas

### Do módulo de ETL (já aplicados)

| Padrão | Aplicação em Notifications |
|--------|---------------------------|
| **Repository** | `envio_repository.py` encapsula SQL de envios |
| **Pydantic Settings** | `settings.py` centraliza toda configuração |
| **Hierarquia de exceções** | `RetryableException` (rede, SMTP) vs `NonRetryableException` (template, validação) |
| **Value Objects** | `PhoneNumber` (normalização), `Channel` (enum), `AlertSeverity` |
| **Protocol** | `Sender` protocol para email/whatsapp; `TemplateRenderer` protocol por canal |
| **Logger JSON** | Structured logging com correlation_id por mensagem |
| **Context manager DB** | `get_connection()` com commit/rollback automático |
| **Facade de repositórios** | `infra/database/__init__.py` expõe API unificada |
| **Constants de domínio** | Nomes de fila, status, canais em `domain/constants.py` |

### Novos para este módulo

| Padrão | Motivação |
|--------|-----------|
| **Strategy (Sender)** | Adicionar canais (SMS, push) sem modificar o dispatcher |
| **Strategy (TemplateRenderer)** | Cada canal tem seu renderer; lógica compartilhada na base |
| **Dead-letter queue** | Mensagens que falharam N vezes vão para fila separada para análise |
| **Graceful shutdown** | Consumer captura SIGTERM e finaliza processamento atual antes de parar |
| **Idempotency check** | Antes de registrar envio, verificar se já existe registro para aquele aviso+usuário+canal |

---

## Integrações

| Sistema | Tipo | Finalidade |
|---------|------|-----------|
| Redis | Fila (entrada) | Consumo de `etl:notifications:ready`; dead-letter em `etl:notifications:dead-letter` |
| PostgreSQL | Banco de dados | Consulta de usuários e preferências; registro de envios na tabela `envios` |
| SMTP Gmail | E-mail (saída) | Envio de notificações por e-mail (porta 587, TLS) |
| Z-API | HTTP (saída) | Envio de notificações por WhatsApp (`api.z-api.io`) |

> **Nota:** O módulo acessa o banco de dados **diretamente** (sem HTTP para o `modulo_usuarios`). A resolução de usuários e preferências é feita via `infra/database/usuario_repository.py`.

### Contrato de entrada (fila Redis)

Payload publicado pelo ETL em `etl:notifications:ready`:

```json
{
  "execution_id": "uuid",
  "date": "YYYY-MM-DD",
  "avisos_count": 12,
  "alerts": [
    {
      "aviso_id": "uuid",
      "id_cidade": "uuid",
      "id_evento": "uuid",
      "nome_cidade": "Goiânia",
      "nome_evento": "temperatura alta",
      "valor": 42.5,
      "unidade_medida": "°C",
      "horario": "14:00:00",
      "data_referencia": "2026-03-14"
    }
  ]
}
```

> **Nota:** Todos os campos usam snake_case, compatível com `AlertPayload` em `domain/entities.py`.

### Contrato de saída (tabela `envios`)

```sql
INSERT INTO envios (id_canal, id_aviso, id_usuario_destinatario, id_status)
VALUES ($1, $2, $3, $4)
```

---

## Status de Implementação

### Fase 1 — Fundação ✅ Concluída

- [x] Criar estrutura de diretórios (`domain/`, `application/`, `infra/`)
- [x] Configurar `pyproject.toml` com dependências versionadas
- [x] Implementar `settings.py` com Pydantic Settings
- [x] Implementar `domain/constants.py`, `domain/exceptions.py`
- [x] Implementar logger JSON estruturado
- [x] Implementar `infra/database/postgres.py` + `envio_repository.py`

### Fase 2 — Domain e Application ✅ Concluída

- [x] Definir entidades (`AlertPayload`, `ExecutionPayload`, `UserWithPreference`, `Notification`)
- [x] Definir value objects (`Channel`, `SeverityInfo`, `PhoneNumber`, `Period`)
- [x] Definir protocols (`Sender`, `TemplateRenderer`)
- [x] Implementar `application/resolver.py`
- [x] Implementar `application/filter.py`
- [x] Implementar templates com base compartilhada (`base.py`, `email_renderer.py`, `whatsapp_renderer.py`)
- [x] Implementar `application/dispatcher.py`

### Fase 3 — Infrastructure ✅ Concluída

- [x] Implementar `infra/senders/email_sender.py`
- [x] Implementar `infra/senders/whatsapp_sender.py`
- [x] Implementar `infra/redis/queue_consumer.py`
- [x] Implementar repositórios de banco (`usuario_repository`, `catalogo_repository`, `envio_repository`)

### Fase 4 — Integração e Consumer ✅ Concluída

- [x] Implementar `application/consumer.py` (orquestrador principal)
- [x] Implementar `main.py`
- [x] Configurar Dockerfile e docker-compose.yml

### Fase 5 — Validação 🔄 Em andamento

- [x] Testes unitários em domain e application (`tests/`)
- [ ] Graceful shutdown no consumer (SIGTERM → aguarda processamento atual)
- [ ] Health check detectável pela orquestração (Docker/Kubernetes)
- [ ] Teste end-to-end: ETL publica → Notifications consome → envio registrado
- [ ] Comparação de comportamento com módulo legado (`backend/modulo_envios`)
- [ ] Resolver dependência do threshold de temperatura (ver `documentacao/tasks.md`)
- [ ] Cutover: desativar `backend/modulo_envios` e passar tráfego para este módulo
