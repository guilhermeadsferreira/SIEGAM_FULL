# Fluxo do Módulo de Alertas

Este documento descreve o fluxo de execução do módulo de alertas, responsável por baixar, processar dados meteorológicos e gerar alertas.

1.  **Inicialização e Limpeza:**
    *   O script principal (`alert_generator.py`) é executado.
    *   A função `clean_old_files` de `file_utils.py` é chamada para remover arquivos temporários e de dados de dias anteriores, como `.ctl`, `.gra`, `.out` e `.processed`.

2.  **Aquisição de Dados Meteorológicos:**
    *   A função `download_meteogram_file` em `file_utils.py` baixa o arquivo de previsões meteorológicas (`HST*-MeteogramASC.out`) do servidor do CEMPA (Centro de Excelência em Meteorologia do Piauí).
    *   O arquivo baixado contém dados brutos de previsão para diversas localidades (polígonos).

3.  **Parsing dos Dados:**
    *   A classe `MeteogramParser` é instanciada com o caminho do arquivo baixado.
    *   O método `parse()` lê o arquivo, extrai os dados meteorológicos (temperatura, umidade, vento, chuva, etc.) para cada localidade e os organiza em uma estrutura de dados em memória.

4.  **Geração de Alertas:**
    *   A classe `AlertGenerator` utiliza os dados parseados para verificar se alguma condição de alerta foi atingida.
    *   São executadas as seguintes verificações:
        *   `check_temperature_alerts`: Compara a temperatura máxima e mínima com os limiares definidos em um arquivo de configuração (`config.csv`).
        *   `check_humidity_alerts`: Verifica se a umidade relativa está abaixo de um limiar mínimo.
        *   `check_wind_alerts`: Verifica se a velocidade do vento ultrapassa um limiar.
        *   `check_rain_alerts`: Verifica se a precipitação excede um limiar.
    *   Os alertas gerados são armazenados na memória.

5.  **Integração com a API de Usuários:**
    *   O `UsuarioApiClient` é utilizado para se comunicar com o sistema de gerenciamento de usuários.
    *   **Autenticação:** O cliente realiza o login na API (`/usuarios/login`) para obter um token de autenticação.
    *   **Busca de Dados:** O cliente obtém a lista de "eventos" (tipos de alerta) e "cidades" cadastrados na API.

6.  **Formatação e Envio dos Alertas:**
    *   Os alertas gerados no passo 4 são formatados pela função `get_import_request` para o padrão esperado pela API (DTO - Data Transfer Object).
    *   A lista de alertas formatados é enviada em um único lote para o endpoint `/avisos/lote` da API através da função `importar_avisos`.

7.  **Controle de Execução:**
    *   Após o processamento (com sucesso ou falha), a função `create_control_file` cria um arquivo de controle (ex: `HST...processed`).
    *   Este arquivo serve como um marcador para impedir que o mesmo arquivo de dados seja processado novamente no mesmo dia.

8.  **Finalização:**
    *   O script exibe um resumo dos alertas e o tempo total de execução.
