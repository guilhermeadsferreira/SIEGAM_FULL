# Módulo Envios

Serviço responsável por gerenciamento de alertas e envio de notificações.  
Utiliza **FastAPI**, **Redis** e consumidores assíncronos para processar filas de envio (WhatsApp, e-mail e integrações externas).

---

## 📋 Visão Geral

O módulo é composto por:

- API FastAPI para criação, consulta e disparo de alertas.
- Produtores que inserem mensagens nas filas Redis.
- Consumidores que processam as notificações.
- Serviços especializados (WhatsApp, e-mail, templates, integrações externas).
- Schemas Pydantic para validação.
- Suporte completo a variáveis de ambiente (.env).

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|-----------|-----|
| **Python 3.11** | Linguagem principal |
| **FastAPI** | Framework da API |
| **Uvicorn** | Servidor ASGI |
| **Redis** | Filas distribuídas |
| **Pydantic** | Schemas e validação |
| **python-dotenv** | Gestão de variáveis ambiente |
| **Docker / Docker Compose** | Execução e deploy |

---

## 📂 Estrutura do Projeto

```
src/
├── main.py                           # API principal FastAPI
├── config.py                         # Configurações gerais e Redis
├── Dockerfile                        # Build containerizado
├── __init__.py
│
├── consumers/                        # Workers que processam filas
│   └── notification_consumer.py
│
├── models/                           # Schemas e modelos Pydantic
│   ├── alert_model.py
│   └── city_alerts_model.py
│
├── producers/                        # Funções que enfileiram mensagens
│   ├── notification_producer.py
│   └── __init__.py
│
├── routes/                           # Rotas HTTP da API
│   └── alerts_routes.py
│
├── services/                         # Lógica de negócio e integrações
│   ├── alert_service.py
│   ├── email_service.py
│   ├── external_integration_service.py
│   ├── template_service.py
│   ├── whatsapp_service.py
│   └── __init__.py
│
└── templates/                        # Templates de e-mail e WhatsApp
    ├── email_template_service.py
    ├── whatsapp_template_service.py
    └── __init__.py
```

---

## ⚙️ Variáveis de Ambiente (.env)

Exemplo de `.env`:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email API
EMAIL_API_URL=https://api.email.com/send

# WhatsApp API
WHATSAPP_API_URL=https://api.whatsapp.com/send
WHATSAPP_CLIENT_TOKEN=seu_token_aqui
```

O carregamento é automático via `python-dotenv`.

---

## 🚀 Instalação e Ambiente Local

### Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate   # PowerShell: .venv\Scripts\Activate.ps1
```

### Instalar dependências

```bash
pip install -r requirements.txt
```

---

## ▶️ Executando a API

### Modo Desenvolvimento

```bash
uvicorn src.main:app --reload
```

- **Swagger:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Executando com Docker

#### Build

```bash
docker build -t modulo_envios .
```

#### Run

```bash
docker run -p 8000:8000 modulo_envios
```

#### Docker Compose

```bash
docker compose up --build
```

---

## 🔄 Executando os Consumers

Os consumers processam as mensagens de alerta enviadas para o Redis.

```bash
python src/consumers/notification_consumer.py
```

**Nota:** Eles devem ser executados separadamente da API.

---

## 📊 Fluxo de Processamento

1. Uma rota HTTP recebe um alerta (via `alerts_routes.py`).
2. O serviço (`alert_service.py`) valida e cria o evento.
3. O produtor insere a tarefa no Redis.
4. O consumer correspondente escuta a fila e processa a notificação.
5. O serviço de envio (WhatsApp, e-mail, integração externa) dispara a mensagem.
6. Logs e exceções são registrados conforme necessário.

---

## 📋 Scripts Auxiliares

| Comando | Descrição |
|---------|-----------|
| `uvicorn src.main:app --reload` | Inicia a API em modo dev |
| `docker build -t modulo_envios .` | Build Docker |
| `docker run -p 8000:8000 modulo_envios` | Sobe container |
| `python src/consumers/notification_consumer.py` | Executa consumer |

---

## ➕ Como adicionar um novo canal de comunicação (ex.: SMS)

Esta seção descreve, passo a passo, como adicionar um novo canal de comunicação à aplicação. O foco aqui é na criação do template dinâmico (estrutura, sanitização e agrupamento) mantendo a lógica de níveis e agrupamento de avisos por cidade. O próximo passo (implementação do serviço de envio) está listado ao final como título, mas não será detalhado aqui.

Pré-requisito: já existem os templates `email` e `whatsapp` em `src/services/templates/` e a fachada `TemplateService` em `src/services/template_service.py` — esses arquivos servem de referência.

1) Entender o formato de entrada para templates
- Os templates recebem `cidades_alertas`: lista de objetos com a forma usada hoje pelos templates:
  - `cidade`: string (nome)
  - `uf`: string
  - `alertas`: lista de alertas, cada alerta contendo ao menos:
    - `eventoNome` (ou `evento.nome` quando originário do `AlertService`) — nome do evento
    - `valor` — valor observado
    - `dataReferencia` — data em ISO `YYYY-MM-DD`
    - `unidadeMedida` — por exemplo `%`, `mm`, `km/h`, `°C`
    - `periodo` — string do período (ex: `08:00-12:00`)

2) Regras gerais que o template deve respeitar
- Agrupar alertas por cidade (mesma organização dos templates existentes).
- Não mover lógica de decisão (quem recebe) para templates: a filtragem por preferência e limiares fica em `AlertService`.
- Templates devem apenas formatar a apresentação (text/html/plain) para o canal.

3) Requisitos especiais do canal SMS (exemplo)
- SMS não aceita HTML: remova tags HTML antes de gerar a mensagem.
- SMS tende a não aceitar acentos e emojis de forma confiável em todos os provedores: normalize para ASCII (use `unicodedata.normalize` e encode/decode) e remova emojis/caracteres não-ASCII.
- Limite de tamanho: por padrão 160 caracteres por segmento. O template pode retornar uma única string longa (o serviço de envio pode segmentar) ou já devolver uma lista de segmentos.

4) Exemplo de implementação de template SMS

Crie `src/services/templates/sms_template_service.py` com a estrutura dos demais templates com header, body e footer. Sendo o Body personalizado para cada tipo de aviso e nível.


5) Registrar o novo template em `TemplateService`

- Abra `src/services/template_service.py` e adicione o novo serviço ao dicionário `self.services`:

```python
from .templates.sms_template_service import SMSTemplateService

class TemplateService:
    def __init__(self):
        self.services = {
            "email": EmailTemplateService(),
            "whatsapp": WhatsAppTemplateService(),
            "sms": SMSTemplateService(),
        }
```

Observação: `generate_template` espera que `canal` seja um dict com `nomeCanal`, por exemplo `{"nomeCanal": "sms"}`. Ao produzir mensagens para fila, mantenha essa forma.


## 🛠️ Como adicionar um serviço de envio (ex.: `smsSender`)

Esta seção descreve as modificações necessárias para adicionar o componente responsável pelo envio real (provider) — aqui chamado `smsSender`. Inclui exemplo de implementação, variáveis de ambiente recomendadas e onde integrar o serviço no consumer.

1) Arquivo do serviço
- Crie `src/services/sms_service.py` (nome sugerido) com a API mínima compatível com os outros serviços (`send_bulk(usuarios, conteudo)` e `send(destinatarios, conteudo)`).

2) Variáveis de ambiente sugeridas (ou o que mais for necessário)
- `SMS_API_URL` – endpoint do provider de SMS
- `SMS_API_KEY` – chave/credencial do provider

3) Integrar no `NotificationConsumer`
- No `src/consumers/notification_consumer.py`, importe: 
```python
from src.services.sms_service import SMSSenderService

class NotificationConsumer:
    def __init__(self):
        # ... já existente
        self.email_service = EmailService()
        self.whatsapp_service = WhatsAppService()
        self.sms_service = SMSSenderService()  # nova linha
        self.external_integration_service = ExternalIntegrationService()
```

- Em `process_notification`, adicione o ramo para `sms` (seguindo o padrão dos demais canais):

```python
        if nomeCanal.lower() == "email":
            self.email_service.send_bulk(usuarios, conteudo)
        elif nomeCanal.lower() == "whatsapp":
            self.whatsapp_service.send_bulk(usuarios, conteudo)
        elif nomeCanal.lower() == "sms":
            self.sms_service.send_bulk(usuarios, conteudo)
        else:
            print(f"[NotificationConsumer] Canal {nomeCanal} não suportado.")
            return
```

4) Boas práticas de implementação
- Normalize números (adicione prefixo de país quando necessário).
- Trate limites de tamanho (160 chars) e possibilite segmentação caso o provider não o faça.
- Mantenha logs claros para retrace (quem recebeu, status do provider, erros).
- Respeite o fluxo de registro de envios já implementado (o `NotificationConsumer` chama `register_envios` por `idAviso`), portanto não duplique essa lógica no serviço de envio.

Observação : Para outros tipos de canais de comunicação os passos serão os mesmo, desde a geração de templates ao serviço de envios.

