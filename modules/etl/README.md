# SIEGAM ETL Module

Este projeto é responsável pelo processo de ETL (Extract, Transform, Load) de dados meteorológicos do sistema SIEGAM. Ele opera de forma assíncrona para coletar meteogramas, transformar os dados brutos e analisar condições para geração de alertas.

## Índice

- [Pré-requisitos](#pré-requisitos)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Configuração do Ambiente com UV](#configuração-do-ambiente-com-uv)
- [Bibliotecas Principais](#bibliotecas-principais)
- [Arquitetura e Celery](#arquitetura-e-celery)
- [Gerenciamento de Erros e Logs](#gerenciamento-de-erros-e-logs)
- [Execução com Docker](#execução-com-docker)
- [Execução Local (Desenvolvimento)](#execução-local-desenvolvimento)
- [Estrutura de Diretórios](#estrutura-de-diretórios)

## Pré-requisitos

Para executar este projeto, você precisará das seguintes ferramentas instaladas:

*   **Python 3.12+**: Linguagem base do projeto.
*   **Docker & Docker Compose**: Para execução isolada dos serviços (Redis, Worker).
*   **UV**: Gerenciador de pacotes e projetos Python de alta performance.

## Variáveis de Ambiente

As configurações do projeto são controladas via variáveis de ambiente. Copie o arquivo `.env.example` para `.env` e ajuste conforme necessário.

### Configuração Geral
| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Ambiente de execução (`development`, `staging`, `production`). | `development` |
| `HTTP_TIMEOUT` | Tempo máximo (em segundos) para requisições HTTP de download. | `30.0` |
| `MIN_FILE_SIZE_BYTES` | Tamanho mínimo (em bytes) para considerar um download válido. | `100` |

### Celery e Redis
| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `REDIS_URL` | URL de conexão com o Redis (Broker e Backend). | `redis://localhost:6380/0` |
| `CELERY_MAX_RETRIES` | Número máximo de tentativas de reexecução para tasks falhas. | `3` |
| `CELERY_RETRY_BACKOFF_MAX` | Tempo máximo de espera (backoff) entre tentativas. | `60` |

### Agendamento e Fonte de Dados
| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `METEOGRAM_BASE_URL` | URL base para download dos arquivos de meteograma. | `https://tatu.cempa.ufg.br/...` |
| `METEOGRAM_BASE_PATH` | Caminho local para armazenamento temporário dos arquivos. | `tmp/meteograms` |
| `ETL_SCHEDULE_HOUR` | Hora do dia para execução agendada do ETL (0-23). | `6` |
| `ETL_SCHEDULE_MINUTE` | Minuto da hora para execução agendada do ETL (0-59). | `0` |

## Configuração do Ambiente com UV

Este projeto utiliza o [uv](https://github.com/astral-sh/uv) para gerenciamento de dependências.

### 1. Instalação do UV

Caso ainda não tenha o `uv` instalado:

```bash
# MacOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Comandos Principais

*   **Criar ambiente virtual**:
    ```bash
    uv venv
    ```
*   **Ativar ambiente virtual**:
    ```bash
    # Linux/macOS
    source .venv/bin/activate

    # Windows
    .venv\Scripts\activate
    ```
*   **Sincronizar dependências** (instala tudo que está no `uv.lock`):
    ```bash
    uv sync
    ```
*   **Adicionar nova biblioteca**:
    ```bash
    uv add <nome_da_lib>
    ```
*   **Listar dependências em árvore**:
    ```bash
    uv tree
    ```

### 3. Configuração Inicial

Para configurar o ambiente de desenvolvimento do zero:

```bash
# 1. Clone o repositório e entre na pasta
cd modules/etl

# 2. Crie o ambiente virtual e instale as dependências
uv sync

# 3. Ative o ambiente (opcional se usar 'uv run')
source .venv/bin/activate
```

## Bibliotecas Principais

Abaixo estão as principais bibliotecas utilizadas e seus papéis no sistema:

| Biblioteca | Função Principal |
| :--- | :--- |
| **celery** | Orquestração de tarefas assíncronas e agendadas (Distributed Task Queue). |
| **redis** | Broker de mensagens utilizado pelo Celery e backend de resultados. |
| **httpx** | Cliente HTTP moderno e assíncrono para realizar o download dos meteogramas. |
| **tenacity** | Biblioteca para implementação de retries (tentativas de reexecução) robustos. |
| **pydantic** | (Indireto via FastAPI/Outros) Validação de dados e settings. |

> **Nota**: Este projeto não utiliza `pandas` para transformação de dados, optando por manipulação direta de estruturas de dados Python para manter a performance e simplicidade no contexto específico dos meteogramas.

## Arquitetura e Celery

O núcleo do processamento é baseado no **Celery**. Ele gerencia o fluxo de trabalho dividindo-o em tarefas menores e encadeadas.

### Papel do Celery

O Celery atua como um sistema de filas, permitindo que o download, transformação e análise ocorram de forma assíncrona e escalável. O **Celery Beat** é usado para agendar a execução diária do fluxo.

### Principais Tasks

As tarefas estão definidas principalmente em `main.py` e orquestram a lógica contida na camada `application`.

1.  **`download_file`** (`main.download_file`)
    *   **Gatilho**: Agendado via Celery Beat (diariamente, horário configurável via `.env`).
    *   **Função**: Baixa o arquivo bruto do meteograma da fonte externa.
    *   **Fluxo**: Ao finalizar com sucesso, dispara a task `transform`.

2.  **`transform`** (`main.transform`)
    *   **Gatilho**: Sucesso da task `download_file`.
    *   **Função**: Lê o arquivo bruto baixado e o converte para um formato JSON estruturado e padronizado.
    *   **Fluxo**: Ao finalizar, dispara a task `analyze`.

3.  **`analyze`** (`main.analyze`)
    *   **Gatilho**: Sucesso da task `transform`.
    *   **Função**: Analisa os dados meteorológicos (vento, chuva, temperatura, umidade) aplicando regras de negócio para identificar condições de alerta. Persiste os resultados/alertas.

## Gerenciamento de Erros e Logs

### Tratamento de Erros

As tasks do Celery são configuradas com resiliência em mente:

*   **Retry Automático**: Exceções do tipo `RetryableException` causam uma reexecução automática da task.
    *   Utiliza **Backoff Exponencial** (tempo de espera aumenta entre tentativas).
    *   Limite máximo de tentativas configurável (`CELERY_MAX_RETRIES`).
*   **Falha Definitiva**: Exceções `NonRetryableException` ou erros não tratados interrompem o fluxo imediatamente e registram o erro.

### Logs

*   **Formato**: JSON estruturado (`JsonLogger`), ideal para ingestão por ferramentas de monitoramento (ex: Datadog, CloudWatch).
*   **Saída**: Os logs são enviados para `stdout` (saída padrão), podendo ser visualizados via `docker logs`.
*   **Conteúdo**: Incluem timestamp, nível, mensagem, contexto da task (ID, nome) e stack trace em caso de erro.

## Execução com Docker

O Docker Compose orquestra os serviços necessários (Redis e Worker).

**Principais Comandos:**

*   **Iniciar serviços**:
    ```bash
    docker-compose up -d --build
    ```
    *Inicia o Redis e o Celery Worker (com Beat embutido).*

*   **Acompanhar logs**:
    ```bash
    docker-compose logs -f celery_worker
    ```

*   **Parar serviços**:
    ```bash
    docker-compose down
    ```

*   **Executar comando no container**:
    ```bash
    docker-compose exec celery_worker uv run python run_once.py
    ```

## Execução Local (Desenvolvimento)

Para rodar e testar o projeto em sua máquina durante o desenvolvimento:

1.  **Configurar Variáveis de Ambiente**:
    Copie o arquivo de exemplo e ajuste conforme necessário.
    ```bash
    cp .env.example .env
    ```

2.  **Subir Infraestrutura de Apoio (Redis)**:
    Se não quiser rodar tudo via Docker, suba pelo menos o Redis:
    ```bash
    docker-compose up -d redis
    ```

3.  **Executar o Worker do Celery**:
    Em um terminal separado:
    ```bash
    # Apenas o worker (processa tarefas)
    uv run celery -A main worker --loglevel=info
    
    # Ou Worker + Beat (agendador) juntos
    uv run celery -A main worker --beat --loglevel=info
    ```

4.  **Disparar Tarefa de Teste**:
    Para não esperar o agendamento, você pode disparar o fluxo manualmente usando o script utilitário:
    ```bash
    uv run python run_once.py
    ```
    *Isso enviará uma task `download_file` para a fila imediatamente.*

## Estrutura de Diretórios

Visão geral da organização do projeto:

```
modules/etl/
├── application/        # Lógica de aplicação e casos de uso
│   ├── analyzer/       # Regras de negócio para análise meteorológica
│   ├── download.py     # Lógica de download
│   └── transform.py    # Lógica de transformação de dados
├── domain/             # Núcleo do domínio (Entidades, Value Objects, Exceções)
├── infra/              # Implementações de infraestrutura
│   ├── celery/         # Configurações do Celery
│   └── logger/         # Configuração de logs estruturados
├── main.py             # Entrypoint do Celery (definição das tasks)
├── settings.py         # Configurações centralizadas (carrega .env)
├── run_once.py         # Script auxiliar para disparo manual de tasks
├── docker-compose.yml  # Orquestração de containers
├── Dockerfile          # Definição da imagem Docker
└── pyproject.toml      # Definição de dependências e projeto (UV)
```
