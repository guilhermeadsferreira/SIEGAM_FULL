# Fluxo de Processamento de Alertas

Este documento descreve o fluxo de processamento de alertas da aplicação, desde o recebimento do gatilho inicial até o envio das notificações aos usuários.

## 1. Disparo do Processo

O fluxo é iniciado por uma requisição `POST` ao endpoint `/alerts/start`. Este endpoint é projetado para ser acionado por um agendador de tarefas (como um cron job) ou manualmente por um administrador.

## 2. Coleta de Alertas do Dia

- A função `start_alert_processing` em `src/routes/alerts_routes.py` é executada.
- Ela invoca o `ExternalIntegrationService.get_alerts_for_today()`, que faz uma requisição `GET` a uma API externa para obter a lista completa de alertas meteorológicos previstos para o dia corrente.

## 3. Processamento em Segundo Plano

- Se houver alertas para o dia, a aplicação inicia uma tarefa em segundo plano (`background_tasks.add_task`) para executar o método `alert_service.process_all_alerts`.
- Isso permite que a API retorne uma resposta imediata (`200 OK`), confirmando que o processo foi iniciado, sem precisar esperar a conclusão de todo o processamento.

## 4. Agrupamento de Alertas por Cidade

- Dentro do `AlertService`, o método `process_all_alerts` começa agrupando a lista de alertas recebida por `idCidade`. Isso otimiza as consultas subsequentes.

## 5. Busca de Usuários por Alerta

- O sistema itera sobre cada alerta agrupado.
- Para cada alerta, ele chama o `integration_service.get_users_by_city_and_alert()`. Este método consulta a API externa para obter uma lista de usuários que registraram interesse em receber notificações para aquele tipo de evento (`idEvento`) naquela cidade específica (`idCidade`).

## 6. Agregação de Alertas por Usuário

- O sistema constrói uma estrutura de dados (`users_alerts`) que mapeia cada ID de usuário (`uid`) a um objeto contendo:
    - Os detalhes do usuário (`usuario`).
    - Uma lista de todos os alertas (`alertas`) que são relevantes para ele, com base em suas preferências.

## 7. Geração de Templates e Enfileiramento

- O sistema itera sobre a estrutura `users_alerts`.
- Para cada usuário:
    1.  **Verificação de Canais**: Ele verifica os canais de comunicação preferidos do usuário (ex: `["email", "whatsapp"]`).
    2.  **Geração de Conteúdo**: Para cada canal, ele invoca o `TemplateService.generate_template`. Este serviço atua como uma fachada, selecionando o `EmailTemplateService` ou o `WhatsAppTemplateService` apropriado.
    3.  **Customização**: O serviço de template gera a mensagem (HTML para e-mail, texto formatado para WhatsApp), consolidando todos os alertas do usuário em um único resumo.
    4.  **Enfileiramento**: O `NotificationProducer.send_to_queue` é chamado. Ele cria um payload JSON contendo o canal, os dados do usuário e o conteúdo da mensagem, e o envia para uma fila no Redis chamada `notification_queue`.

## 8. Consumo da Fila e Envio Final

- Um processo separado e contínuo, o `NotificationConsumer`, monitora a fila `notification_queue` no Redis.
- Ao receber uma nova mensagem:
    1.  **Processamento**: O consumidor extrai o payload da mensagem.
    2.  **Seleção do Serviço de Envio**: Com base no `canal` ("email" or "whatsapp"), ele aciona o serviço correspondente (`EmailService` ou `WhatsAppService`).
    3.  **Envio**: O serviço de envio executa a lógica para despachar a notificação. Atualmente, isso é simulado através de requisições `POST` para APIs de envio falsas.

Essa arquitetura com filas e workers desacopla a geração das notificações do envio, tornando o sistema mais resiliente e escalável. Se o serviço de e-mail estiver fora do ar, por exemplo, as notificações de WhatsApp não são afetadas, e as de e-mail podem ser reprocessadas posteriormente.
