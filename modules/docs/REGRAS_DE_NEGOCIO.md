# Regras de Negócio — Pipeline de Alertas Meteorológicos

**Versão:** 1.1
**Data:** 28/03/2026
**Destinatários:** Stakeholders / POs / Revisão Técnica
**Status:** Aguardando validação

---

## 1. Visão Geral

O sistema monitora condições meteorológicas no estado de Goiás com base em dados do CEMPA/UFG e notifica usuários cadastrados quando variáveis climáticas ultrapassam limiares pré-definidos ou personalizados.

O pipeline é dividido em duas etapas principais:

1. **ETL** — Obtém os dados brutos, analisa as variáveis e persiste os alertas.
2. **Notificações** — Lê os alertas, resolve os destinatários, aplica filtros de preferência e envia as mensagens.

```
CEMPA/UFG → [ETL: Download → Transformação → Análise → Carga] → PostgreSQL + Redis
         → [Notificações: Consumo → Resolução → Filtro → Envio] → Usuário Final
```

---

## 2. Origem dos Dados

| Dado | Origem | Formato | Frequência |
|------|--------|---------|------------|
| Meteograma | CEMPA/UFG | Arquivo `.out` (ASC) | Diária |
| Hora de execução | Configuração do sistema | — | Diária às 06h (Brasília) |

O arquivo baixado contém dados de múltiplos polígonos geográficos (regiões/municípios). O sistema filtra apenas os polígonos do **estado de Goiás** e o horizonte de **11h a 35h** a partir da rodada do modelo.

> **Decisão em aberto:** O comportamento quando um polígono do arquivo não possui cidade correspondente no cadastro está indefinido. Atualmente esses polígonos são ignorados e registrados em log.

---

## 3. Tipos de Alertas Suportados

O sistema analisa **5 variáveis meteorológicas** e pode gerar um alerta para cada uma delas por município:

| Tipo de Alerta | Identificador | Unidade |
|----------------|--------------|---------|
| Temperatura alta | `temperatura alta` | °C |
| Temperatura baixa | `temperatura baixa` | °C |
| Umidade baixa | `umidade baixa` | % |
| Vento forte | `vento` | km/h |
| Chuva intensa | `chuva` | mm/h |

---

## 4. Regras de Análise (Geração de Alertas)

### 4.1 Temperatura

- O sistema extrai a temperatura **máxima** e **mínima** prevista para cada município no horizonte analisado.
- Os valores estão originalmente em Kelvin e são convertidos para Celsius (`°C = K − 273,15`).
- Os limiares de disparo são definidos **por município e por mês**, com base em uma tabela de configuração interna (`TemperatureConfig`).

| Condição | Alerta gerado |
|----------|--------------|
| Temperatura máxima > limiar do mês para aquele município | `temperatura alta` |
| Temperatura mínima < limiar do mês para aquele município | `temperatura baixa` |

> **Ponto de revisão:** Os limiares mensais por município estão definidos internamente no sistema. Devem ser revisados e validados com a equipe técnica e os POs para garantir que refletem critérios meteorológicos adequados para cada região.

---

### 4.2 Umidade Relativa

- A umidade relativa não é fornecida diretamente pelo modelo; é **calculada** a partir da temperatura do ar (`Tave`) e da temperatura de ponto de orvalho (`TDave`), usando a fórmula de Magnus:

```
UR (%) = (e(Td) / e(T)) × 100

onde e(T) = 6,112 × exp((17,27 × T) / (T + 237,7))
```

- O sistema encontra o **menor valor de umidade** previsto no horizonte para cada município.

| Condição | Alerta gerado |
|----------|--------------|
| Umidade mínima < 60% | `umidade baixa` |

---

### 4.3 Velocidade do Vento

- O modelo fornece as componentes vetoriais do vento (U e V, em m/s). O sistema calcula a velocidade resultante:

```
Velocidade (km/h) = √(U² + V²) × 3,6
```

- O sistema encontra a **maior velocidade** prevista no horizonte para cada município.

| Condição | Alerta gerado |
|----------|--------------|
| Velocidade máxima > 12 km/h | `vento` |

---

### 4.4 Precipitação (Chuva)

- A variável `PRECmax` no arquivo fonte é **acumulativa** — representa o total de precipitação acumulada desde o início da série, não uma taxa instantânea.
- A resolução temporal dos dados é de **30 minutos**; a análise é realizada em base **horária**.
- Para cada passo de tempo T, o sistema calcula a **chuva efetiva da última hora** como a diferença entre o valor acumulado em T e o valor acumulado em T−2 (dois passos de 30 min = 1 hora):

```
chuva_horária(T) = PRECmax(T) − PRECmax(T−2)
```

- Valores negativos resultantes de anomalias no dado são tratados como zero.
- Os dois primeiros passos de tempo de cada série são ignorados (T−2 não disponível).
- O sistema encontra a **maior chuva horária** prevista no horizonte para cada município.

| Condição | Alerta gerado |
|----------|--------------|
| Maior chuva horária > 15 mm/h | `chuva` |

> **Decisão em aberto:** Alertas de chuva estavam **desativados** no módulo legado. É necessário confirmar com os POs se o tipo `chuva` deve estar ativo no sistema atual antes de habilitar notificações para esse evento.

---

## 5. Persistência dos Alertas

Após a análise, cada alerta gerado é registrado na tabela `avisos` do banco de dados com as seguintes informações:

| Campo | Descrição |
|-------|-----------|
| Município | Cidade onde o alerta foi identificado |
| Tipo de evento | Ex.: "temperatura alta" |
| Valor observado | Ex.: 34,2 °C |
| Valor limite | Limiar que foi ultrapassado |
| Diferença | Quanto ultrapassou o limiar |
| Data de referência | Data/hora prevista do evento |
| Data de geração | Quando o alerta foi criado |

---

## 6. Envio de Notificações

### 6.1 Quem Recebe

Um usuário recebe uma notificação apenas se:

1. Estiver **inscrito** para aquele tipo de evento (`preferencias`) **naquele município** (`id_cidade`).
2. O alerta **passar pelo filtro de preferências** (seção 6.2).
3. Tiver pelo menos **um canal de entrega** configurado (email ou WhatsApp).

---

### 6.2 Filtro de Preferências do Usuário

O sistema suporta dois modos de inscrição por evento/município:

#### Modo padrão (sem personalização)
O usuário recebe o alerta sempre que ele for gerado para o município inscrito. Não há limiar personalizado — o critério é o mesmo da análise.

#### Modo personalizado
O usuário define um **valor de corte próprio**. O alerta é entregue apenas se o valor observado ultrapassar esse corte individual.

As regras de comparação variam por tipo de alerta:

| Tipo de Alerta | Condição para envio (modo personalizado) |
|----------------|------------------------------------------|
| `temperatura baixa` | Valor observado < valor definido pelo usuário |
| `temperatura alta` | Valor observado > valor definido pelo usuário |
| `chuva` | Valor observado > valor definido pelo usuário |
| `umidade baixa` | Valor observado < valor definido pelo usuário |
| `vento` | Valor observado > valor definido pelo usuário |

#### Alertas críticos (sempre entregues)

Independente do modo de personalização, **alertas críticos são sempre enviados**:

| Tipo | Critério de criticidade |
|------|------------------------|
| `temperatura alta` | Sempre crítico |
| `temperatura baixa` | Sempre crítico |
| `chuva` | Sempre crítico |
| `vento` | Velocidade ≥ 30 km/h |
| `umidade baixa` | Umidade ≤ 30% |

> **Ponto de revisão:** A regra de criticidade para `vento` e `umidade baixa` sobrescreve a personalização do usuário. Confirmar se essa é a intenção e se os valores de 30 km/h e 30% são os corretos.

---

### 6.3 Canais de Entrega

O sistema suporta dois canais:

| Canal | Método | Formato |
|-------|--------|---------|
| Email | SMTP (Gmail) | HTML com identidade visual CEMPA |
| WhatsApp | Z-API | Texto formatado com emojis |

O usuário pode ter um ou ambos os canais ativos. O sistema envia para todos os canais configurados.

---

### 6.4 Conteúdo das Notificações

As mensagens são agrupadas **por município** e incluem, para cada alerta:

- Tipo do evento
- Data e período de ocorrência prevista
- Valor observado com unidade
- Nível de severidade (veja seção 6.5)
- Mensagem contextualizada ao tipo de alerta

As mensagens também incluem um link para que o usuário **gerencie suas preferências** (alterar canais, limiares personalizados, etc.).

---

### 6.5 Níveis de Severidade

A severidade é usada para colorir e contextualizar as mensagens. Cada tipo de alerta possui sua tabela própria:

#### Umidade Baixa

| Faixa | Nível | Mensagem |
|-------|-------|----------|
| 31% – 60% | Crítico | Crítico para a saúde humana |
| 21% – 30% | Atenção | Estado de Atenção |
| 12% – 20% | Alerta | Estado de Alerta |
| Abaixo de 12% | Emergência | Estado de Emergência |

#### Vento

| Faixa | Nível |
|-------|-------|
| 12 – 20 km/h | Brisa fraca |
| 20 – 30 km/h | Brisa moderada |
| 30 – 40 km/h | Ventania |
| 40 – 50 km/h | Forte ventania |
| Acima de 50 km/h | Vento forte |

#### Chuva

| Faixa | Intensidade |
|-------|-------------|
| 15 – 25 mm/h | Moderada |
| Acima de 25 mm/h | Forte |

#### Temperatura

- Sempre classificada como evento de alta severidade (cor vermelha).
- Não há subdivisão de níveis.

---

## 7. Controle de Duplicidade

O sistema garante que **um mesmo alerta não seja entregue duas vezes** para o mesmo usuário no mesmo canal. O controle é feito por registro de entrega na tabela `envios`, verificado antes de cada envio.

---

## 8. Tratamento de Falhas e Reprocessamento

| Situação | Comportamento |
|----------|--------------|
| Falha de rede (download/envio) | Reprocessado automaticamente até 3 vezes com espera crescente |
| Arquivo corrompido ou inválido | Falha permanente — não reprocessado |
| Mensagem de alerta com falha de envio | Movida para fila de mensagens mortas (`dead-letter`) para análise manual |
| Erro de banco de dados | Reprocessado automaticamente |

---

## 9. Rastreabilidade

Cada execução diária possui um identificador único (`execution_id`) que permite rastrear:

- Qual arquivo foi baixado
- Quais alertas foram gerados e para quais municípios
- Quais usuários foram notificados e em qual canal
- Qual foi o resultado de cada entrega (sucesso ou falha)

---

## 10. Pontos em Aberto para Revisão

Os itens abaixo requerem decisão dos stakeholders antes de serem finalizados no sistema:

| # | Ponto | Impacto |
|---|-------|---------|
| 1 | Limiares de temperatura por município/mês devem ser validados | Define quando alertas de temperatura são gerados |
| 2 | Alertas de chuva (`chuva`) estavam desativados no sistema legado — confirmar status | Pode habilitar envio de notificações de chuva para todos os inscritos |
| 3 | Municípios sem correspondência no cadastro são ignorados — confirmar comportamento esperado | Alertas de regiões não cadastradas são silenciados sem aviso ao usuário |
| 4 | Criticidade de vento (30 km/h) e umidade (30%) como overrides de personalização — confirmar valores | Usuários com limiar personalizado acima desses valores ainda receberão o alerta |
| 5 | Desligamento seguro e health check do consumidor de notificações não está implementado | Risco de perda de mensagens em reinicializações do serviço |
| 6 | Regra de idempotência na tabela `avisos` (evitar duplicatas no banco) não está definida | Uma execução com falha parcial pode reinserir alertas já existentes |
