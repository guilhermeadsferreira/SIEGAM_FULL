# ETL — Definição do Módulo

## Papel

Processar dados meteorológicos do CEMPA/UFG, gerar alertas com base em regras climáticas e disponibilizar os avisos para notificação.

## Responsabilidades

- **Extrair** meteogramas ASC de fonte externa (CEMPA/UFG) via HTTP
- **Transformar** arquivos ASC em JSON estruturado, filtrando por janela de tempo e estado (GO)
- **Analisar** condições meteorológicas e gerar alertas quando thresholds são violados
- **Persistir** avisos no banco de dados, mapeando polígonos para cidades e alertas para eventos
- **Despachar** avisos para a fila de notificações via Redis

## Fluxo

```
Download → Transform → Analyze → Load → Dispatch
```

| Etapa | Entrada | Saída |
|-------|---------|-------|
| **Download** | URL externa (CEMPA) | Arquivo ASC local |
| **Transform** | Arquivo ASC | JSON estruturado por polígono |
| **Analyze** | JSON estruturado | Alertas em memória |
| **Load** | Alertas + catálogos (cidades/eventos) | Registros na tabela `avisos` |
| **Dispatch** | Alertas persistidos | Evento na fila Redis |

Cada etapa é uma task Celery independente. O sucesso de uma dispara a próxima via `.delay()`.

**Agendamento:** execução diária às 06:00 (America/Sao_Paulo) via Celery Beat.

## Regras de Negócio

### Download
- Arquivo esperado: `HST{YYYYMMDD}00-MeteogramASC.out`
- Tamanho mínimo para validação: 100 bytes
- Erros de rede disparam retry automático (backoff exponencial, máx. 3 tentativas)

### Transformação
- Janela de tempo: 11h a 35h (39.600s a 126.000s)
- Filtro de estado: apenas polígonos de GO
- Colunas extraídas: Tmax, Tmin, Tave, TDave, Umax, Vmax, PRECmax, entre outras

### Análise

| Variável | Condição de alerta | Threshold |
|----------|-------------------|-----------|
| Umidade relativa | Abaixo do limite | 60% |
| Velocidade do vento | Acima do limite | 12 km/h |
| Taxa de chuva | Acima do limite | 15 mm/h |
| Temperatura | Máxima e mínima extremas | A definir |

**Conversões aplicadas:**
- Temperatura: Kelvin → Celsius (descarta valores fora de 200–350 K)
- Umidade: fórmula de Magnus (Tave, TDave), clamp 0–100%
- Vento: `√(U² + V²) × 3.6` km/h (descarta se componente > 100 ou resultado > 200 km/h)

### Carga
- Polígonos são mapeados para cidades via normalização de nome (NFKD, ASCII, lowercase)
- Alertas são mapeados para eventos cadastrados no banco
- Polígonos ou alertas sem correspondência são registrados como `unmatched`
- Catálogos de cidades e eventos não podem estar vazios

## Integrações

| Sistema | Tipo | Finalidade |
|---------|------|-----------|
| CEMPA/UFG | HTTP (saída) | Download dos meteogramas |
| PostgreSQL | Banco de dados | Persistência de avisos, leitura de cidades e eventos |
| Redis | Broker + fila | Orquestração Celery e fila `etl:notifications:ready` |
| Módulo de Notificações | Fila Redis (saída) | Consumo dos avisos publicados |
