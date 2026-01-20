# SIGEDAM V2 - Backend

Bem-vindo ao repositório central do backend do **Sistema de Geração e Divulgação de Avisos Meteorológicos (SIGEDAM) - Versão 2.0**.

## 🏗️ Arquitetura e Estratégia Modular

A arquitetura do sistema foi desenhada para resolver gargalos de performance e garantir a resiliência do envio de avisos críticos. O backend não é um monólito; ele é composto por **três módulos independentes** que operam em contêineres Docker distintos

### Por que separamos em módulos?

Conforme detalhado na documentação arquitetural do projeto, a separação visa isolar cargas de trabalho com naturezas distintas:

1.  **Isolamento de Recursos:** O processamento de dados meteorológicos (pesado em CPU/Memória) não deve impactar a performance da API de gestão de usuários (crítica para UX).
2.  **Resiliência:** Uma falha na integração com o WhatsApp ou E-mail (Módulo Envios) não deve derrubar o sistema de login ou cadastro (Módulo Usuários).
3.  **Escalabilidade Seletiva:** Em momentos de crise climática, podemos escalar horizontalmente apenas os *workers* de envio de mensagens, sem gastar recursos duplicando o módulo de processamento de arquivos.
4.  **Adequação Tecnológica:** Utilizamos a "ferramenta certa para o trabalho certo". Python para dados, Java para robustez transacional e Python Async para I/O intensivo.

---

## 📦 Visão Geral dos Módulos

Abaixo, uma breve descrição de cada módulo. Para detalhes de instalação, variáveis de ambiente e endpoints, acesse o README específico dentro de cada pasta.

### 1. [Módulo de Alertas](./modulo_alertas) ⛈️
* **Papel:** O "Cérebro Analítico".
* **Responsabilidade:** Realizar o download de arquivos pesados do CEMPA, processar milhões de linhas de dados meteorológicos, aplicar regras de negócio (limiares de chuva, vento, temperatura) e identificar a necessidade de um aviso.
* **Stack Principal:** Python 3.10+.
* **Bibliotecas Chave:** Pandas, NumPy.
* **Tipo de Execução:** *CronJob* / *Script* periódico.

### 2. [Módulo de Usuários](./modulo_usuarios) 👥
* **Papel:** A "Fonte da Verdade" e Gestão de Identidade.
* **Responsabilidade:** Centralizar o acesso ao banco de dados (PostgreSQL), gerenciar autenticação (Auth/JWT), cadastrar usuários e, crucialmente, gerenciar as **preferências complexas** de recebimento de avisos.
* **Stack Principal:** Java 17.
* **Framework:** Quarkus.
* **Persistência:** Hibernate / JPA.
* **Tipo de Execução:** API RESTful.

### 3. [Módulo de Envios](./modulo_envios) 🚀
* **Papel:** O "Núcleo Resiliente" e Comunicação.
* **Responsabilidade:** Receber a ordem de aviso, consultar quem deve receber (comunicando-se com o Módulo de Usuários), gerar os templates e despachar mensagens de forma assíncrona para WhatsApp, SMS e E-mail.
* **Stack Principal:** Python 3.10+.
* **Framework:** FastAPI + Redis Queue (RQ).
* **Infraestrutura de Apoio:** Redis (para gestão de filas).
* **Tipo de Execução:** API (Produtor) + Workers (Consumidores).

---

## 🛠️ Stack Tecnológica Global

Embora cada módulo tenha suas especificidades, a infraestrutura compartilhada utiliza:

| Tecnologia | Função | Motivo da Escolha |
| :--- | :--- | :--- |
| **Docker & Compose** | Orquestração | Garante que o ambiente de dev seja idêntico à VM do LAMCAD e facilita a orquestração dos serviços. |
| **PostgreSQL** | Banco de Dados | Robustez para dados relacionais, suporte ACID e base da "Fonte da Verdade". |
| **Redis** | Broker de Mensagens | Alta performance para filas de envio e desacoplamento entre geração e envio. |

## 🚀 Como Executar (Ambiente de Desenvolvimento)

Como o projeto é containerizado, a recomendação é subir todo o ecossistema via Docker Compose na raiz do projeto (onde este arquivo se encontra).

### Pré-requisitos
* Docker
* Docker Compose

### Passos
1.  Configure as variáveis de ambiente (`.env`) em cada sub-módulo conforme seus respectivos READMEs.
2.  Na raiz, execute:

```bash
docker-compose up --build
```
Isso irá iniciar a orquestração dos serviços:

1. Subir o banco PostgreSQL e o Redis.

2. Compilar e subir a API Java (Módulo Usuários).

3. Subir a API e os Workers Python (Módulo Envios).

4. O Módulo Alertas aguardará o agendamento (cron) ou pode ser executado manualmente via comando Docker.