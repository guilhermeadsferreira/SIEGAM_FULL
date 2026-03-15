## Teste Integrado — ETL → Notifications (WhatsApp)

> Roteiro para testar a integração entre o ETL e o módulo de notificações, focando **apenas envio por WhatsApp** em ambiente de desenvolvimento.

---

### 1. Objetivo do teste

- Verificar se um aviso gerado pelo ETL percorre todo o fluxo até ser enviado via WhatsApp e registrado na tabela de `envios`.
- Garantir que, para os usuários de teste, **somente o canal WhatsApp** seja utilizado (nenhum e-mail disparado).

---

### 2. Pré‑requisitos

- **Infraestrutura:**
  - PostgreSQL acessível pelos módulos ETL e Notifications (mesmo banco usado no desenvolvimento).
  - Redis acessível pelos dois módulos.
- **Configuração do módulo Notifications (`.env`):**
  - `DATABASE_URL` apontando para o banco acima.
  - `REDIS_URL` apontando para o Redis acima.
  - Credenciais **válidas** de WhatsApp (Z‑API):
    - `WHATSAPP_INSTANCE`
    - `WHATSAPP_TOKEN`
    - `WHATSAPP_CLIENT_TOKEN`
  - Para este teste, o SMTP pode ficar configurado com valores “dummy” se não houver intenção de testar e‑mail.
- **Dados de usuário de teste:**
  - Pelo menos um usuário cadastrado com:
    - Número de WhatsApp válido.
    - Preferência de canal contendo **apenas** WhatsApp (sem e‑mail habilitado).

---

### 3. Preparação dos dados de teste

1. **Criar/garantir usuário de teste** no banco:
   - Com cidade associada a pelo menos um dos avisos que o ETL irá gerar.
   - Com preferência de evento compatível (ex.: “temperatura alta”, “chuva”, etc.).
   - Com canais preferidos contendo somente WhatsApp, por exemplo:
     - `canais_preferidos = [{"id": "<id_whatsapp>", "nomeCanal": "whatsapp"}]`
2. (Opcional) Isolar o usuário de teste:
   - Usar uma cidade específica apenas para esse usuário.
   - Facilita rastrear o fluxo no log e no banco.

---

### 4. Passos do teste integrado

1. **Subir o ETL**
   - Usar o `docker-compose.yml` do módulo ETL ou o comando principal (`python main.py` ou tarefa equivalente).
   - Verificar nos logs que as etapas de Download, Transform e Load rodaram com sucesso.
   - Confirmar que a tabela `avisos` recebeu novos registros.

2. **Subir o módulo Notifications**
   - Garantir que o `.env` do módulo está configurado com:
     - `DATABASE_URL` e `REDIS_URL` corretos.
     - Credenciais de WhatsApp válidas.
   - Subir o serviço (via `docker-compose` ou `python main.py` no diretório `modules/notifications`).
   - Nos logs, verificar que o consumer está conectado ao Redis e aguardando mensagens.

3. **Disparar um processamento do ETL**
   - Rodar novamente o ETL para o dia de teste (ou forçar um reprocessamento).
   - Confirmar no log do ETL que um payload foi publicado na fila `etl:notifications:ready`.

4. **Acompanhar o consumo no Notifications**
   - Nos logs do Notifications, verificar:
     - `Payload sem alertas` **não** aparece para esse execution_id.
     - Mensagens indicando que usuários foram resolvidos e que o dispatcher foi chamado.
   - Focar nos logs do usuário de teste (id ou nome).

5. **Verificar envio de WhatsApp**
   - Checar, no dispositivo configurado para o usuário de teste, o recebimento da mensagem.
   - Opcionalmente, conferir nas métricas/logs da Z‑API que a requisição foi recebida com sucesso.

6. **Verificar registro na tabela `envios`**
   - Consultar a tabela `envios` filtrando por:
     - `id_usuario_destinatario` do usuário de teste.
     - `id_canal` correspondente ao WhatsApp.
   - Confirmar que há pelo menos um registro com status de sucesso.

---

### 5. Garantindo “apenas WhatsApp”

Para que este teste dispare **somente WhatsApp** para o usuário de teste:

1. **Configurar canais do usuário:**
   - No cadastro do usuário, deixar apenas o canal WhatsApp configurado.
   - Exemplo: não preencher e‑mail ou não incluir o canal “email” em `canais_preferidos`.

2. **Conferir o comportamento do dispatcher**
   - O `DispatcherService` percorre os canais preferidos do usuário e, para cada um, chama o sender correspondente:
     - Quando a lista de canais do usuário contém somente “whatsapp”, apenas o `WhatsAppSender` será acionado.

3. (Opcional) Desabilitar e‑mail em ambiente de teste:
   - Manter as variáveis de SMTP (`SMTP_EMAIL`, `SMTP_PASSWORD`) vazias ou apontando para uma conta de teste.
   - Dessa forma, mesmo que algum usuário tenha e‑mail configurado, qualquer tentativa de envio ficará isolada desse teste.

---

### 6. Critérios de sucesso

- Pelo menos um aviso gerado pelo ETL para a cidade/evento do usuário de teste.
- Mensagem recebida no WhatsApp do usuário de teste, com conteúdo coerente com os alertas do dia.
- Registro correspondente na tabela `envios`, com:
  - `id_usuario_destinatario` do usuário de teste.
  - `id_canal` de WhatsApp.
  - Status de envio bem‑sucedido.

Se algum desses pontos falhar, registrar evidências (logs do ETL, Notifications e Z‑API) e abrir item no `documentacao/tasks.md`.

