# SIGEDAM V2 - Módulo de Alertas

O **Módulo de Alertas** é o componente responsável pelo processamento analítico do sistema. Ele opera como um serviço em *background* (agendado via Cron) que monitora dados meteorológicos, verifica condições críticas baseadas em limiares configuráveis e dispara notificações para o módulo de envios.

## 📂 Estrutura do Projeto

```
modulo_alertas/
├── src/
│   ├── alert_generator.py    # Orquestrador: Monitora, valida regras e dispara alertas
│   ├── config_parser.py      # Leitura e validação do arquivo config.csv
│   ├── file_utils.py         # Gerenciamento de downloads e limpeza de arquivos temporários
│   ├── http_client.py        # Cliente HTTP para integração com o Módulo de Envios
│   ├── meteogram_parser.py   # Parser especializado para os dados do CEMPA
│   └── __init__.py
├── tmp_files/                # Área temporária para manipulação dos dados brutos
├── venv/                     # Ambiente virtual Python
├── .env                      # Variáveis de ambiente e segredos
├── config.csv                # Configuração dos limiares de alerta por cidade
├── fluxo.md                  # Documentação do fluxo de dados
├── poetry.lock               # Lockfile de dependências (Poetry)
├── pyproject.toml            # Definição do projeto (Poetry)
├── requirements.txt          # Dependências do projeto (Pip)
└── run.sh                    # Script de execução (EntryPoint)
```

## ⚙️ Configuração

### 1. Variáveis de Ambiente (.env)

Para que o módulo funcione e se comunique com o restante do sistema, crie um arquivo `.env` na raiz:

```bash
touch .env
```

Adicione as configurações de integração (exemplo):

```env
# URL do Módulo de Envios (Responsável por despachar E-mail/WhatsApp)
NOTIFICATION_API_URL=http://localhost:8000/internal/dispatch

# Diretórios
DOWNLOAD_DIR=./tmp_files
```

### 2. Configuração de Alertas (config.csv)

Os alertas e seus gatilhos são configurados exclusivamente no arquivo `config.csv`. Este arquivo define quais cidades são monitoradas e quais são os limiares de temperatura e umidade para cada mês.

**Exemplo de configuração:**

```csv
polygon_name,display_name,temp_max_jan,temp_max_feb,...,umid_min
0230-Goiania,Goiânia,35,36,...,15
```

**Campos:**
- `polygon_name`: Identificador técnico da região (não alterar).
- `display_name`: Nome apresentado nas notificações.
- `temp_max_[mes]`: Temperatura máxima para disparo de alerta no mês específico.
- `umid_min`: Umidade mínima para disparo de alerta.

**Nota:** Se a temperatura máxima de um mês estiver definida como `0`, o sistema entenderá que não deve monitorar temperatura para aquele mês/cidade.

## 🚀 Como Executar

O módulo é projetado para execução via script Shell, que gerencia o ambiente virtual e os logs.

### Na Máquina Virtual (Produção)

Utilize o script `run.sh`, que garante o carregamento das variáveis e dependências corretas:

```bash
bash run.sh
```

### Execução Manual (Desenvolvimento)

Caso precise rodar apenas o gerador Python para testes:

```bash
# Via Poetry
poetry run python src/alert_generator.py

# Ou ativando o venv manualmente
source venv/bin/activate
python3 src/alert_generator.py
```

## 🆘 Suporte e Troubleshooting

### Como atualizar as configurações das cidades?

Para atualizar os limiares (ex: alterar a temperatura de alerta de uma cidade), edite diretamente o arquivo `config.csv`.

Após salvar a alteração, é recomendável reiniciar o serviço para garantir que a nova configuração seja carregada imediatamente na próxima execução:

```bash
sudo systemctl stop cempa-notify.service && sudo systemctl start cempa-notify.service
```

⚠️ **Importante:** Não altere os nomes das colunas `polygon_name` e `display_name`, pois são chaves de leitura do sistema.

### Problemas Comuns

**O Script não inicia ou falha silenciosamente**
- Verifique se o arquivo `.env` foi criado corretamente.
- Confirme se a pasta `tmp_files` tem permissão de escrita.
- Verifique os logs de execução (geralmente em `cron.log` ou saída do systemd).

**Alertas não chegam ao destino (Integração)**
- Este módulo não envia e-mails diretamente (ele usa `http_client.py`).
- Verifique se o Módulo de Envios está rodando e acessível na URL configurada no `.env`.
- Se o erro for de conexão (Connection Refused), confirme a porta e o IP no `.env`.

**Alertas não são gerados (Regras de Negócio)**
- Verifique o arquivo `config.csv`.
- Confirme se a temperatura do dia realmente ultrapassou o limiar configurado para o mês atual.
- Lembre-se: Se o valor no CSV for `0`, o alerta é ignorado intencionalmente.

**Alerta de temperatura não aparece para cadastro**
- Isso ocorre se a cidade estiver configurada com temperatura `0` em todos os meses no `config.csv`. O sistema entende que aquela região não possui monitoramento térmico disponível.

---

## 🔁 Geração de alertas — Como funciona

O processo de geração de alertas é orquestrado por `src/alert_generator.py`. Resumidamente:

- `load_meteogram_data()`: carrega e mantém em memória os dados do meteograma (dados brutos por polígono/segundos).
- `check_temperature_alerts()`, `check_humidity_alerts()`, `check_wind_alerts()` (e outros `check_*`): cada função analisa os dados relevantes e retorna um dicionário estruturado por cidade (chave = `display_name`) contendo um ou mais tipos de alerta. Cada alerta segue o formato esperado pelos serviços consumidores e templates: pelo menos `value`, `threshold`, `difference`, `date`, `seconds`, `polygon_name`, `unit`.
- `generate_all_alerts()`: chama cada `check_*`, mescla os dicionários retornados (por cidade) em um único `all_alerts`, armazena em `self.alerts` e retorna o resultado final.

A arquitetura separa responsabilidade: os `check_*` detectam ocorrências; a função `generate_all_alerts` apenas agrega os resultados.

## 🛠️ Como adicionar um novo tipo de alerta (passo a passo)

Exemplo: você quer adicionar alertas de vento extremo com lógica específica — a ideia geral é criar `check_wind_special_alerts()` e integrá-lo.

1) Criar a função `check_<nome>` em `src/alert_generator.py`

- Assinatura sugerida:

```python
def check_meu_alerta(self, param_threshold=..., date=None) -> dict:
	"""Retorna dict {display_name: {tipo_alerta: {...}}} """
```

- Boas práticas dentro do `check`:
  - No início, garanta que `self.meteogram_data` esteja carregado; use `self.load_meteogram_data()` quando necessário.
  - Itere `for polygon_name, config_data in self.config_map.items():` e recupere o `display_name` com `self.config.get_display_name(polygon_name)`; pule se não houver `display_name`.
  - Acesse os dados do polígono com `time_data = self.meteogram_data.get(polygon_name)` e itere `for seconds, values in time_data.items():`.
  - Calcule o valor de interesse, compare com limiares e armazene o melhor/mais relevante registro (valor, seconds, date).
  - Ao montar o dicionário de retorno, mantenha o formato padrão dos outros checks (campos `value`, `threshold`, `difference`, `date`, `seconds`, `polygon_name`, `unit`).
  - Retorne apenas cidades com alertas: `return {city: data for city, data in alerts.items() if data}`.

2) Reutilize utilitários existentes

- Use métodos auxiliares já disponíveis no gerador, por exemplo `self.convert_ms2_to_kmh()`, `self.seconds_to_hhmm()` e `self.get_alert_date()` para consistência de formato.

3) Integrar em `generate_all_alerts()`

- Abra `generate_all_alerts()` e adicione a chamada para seu `check_*` junto com os demais:

```python
my_alerts = self.check_meu_alerta()
# depois de obter os outros alerts
for city, alerts in my_alerts.items():
	if city not in all_alerts:
		all_alerts[city] = {}
	all_alerts[city].update(alerts)
```

4) Garantir compatibilidade com consumidores/templates

- Confirme que o nome do tipo de alerta (ex.: `'vento extremo'`) e os campos usados batem com o que `modulo_envios` espera ao montar as mensagens. Campos essenciais: `value`, `threshold`, `difference`, `date`, `seconds`, `polygon_name`, `unit`.
- Também o evento deve estar cadastrado (com o mesmo nome gerado aqui) no módulo de usuários.

5) Testes e validação

- Teste unitário simples: crie um script que carrega o `AlertGenerator` com um `meteogram` de exemplo e execute apenas seu `check_*` para validar saída.
- Execute `generate_all_alerts()` e verifique `self.alerts` e o resumo com `get_alerts_summary()`.
