# Development Plan: hassAqdataWaterSensor (default branch)

*Generated on 2026-04-08 by Vibe Feature MCP*
*Workflow: [epcc](https://mrsimpson.github.io/responsible-vibe-mcp/workflows/epcc)*

## Goal
Script Python que faz scraping do site AqData (sistema.aqdata.com.br) para obter leituras diárias do hidrômetro e envia os dados para o Home Assistant via MQTT.

## Key Decisions
- **Abordagem**: Script Python + cron (não custom HACS integration)
- **Scraping**: Site AqData é PHP/Adianti Framework, sem API REST. Dados obtidos via web scraping com requests + BeautifulSoup
- **Login**: Apenas usuário + senha (sem 2FA)
- **Envio ao HA**: Via MQTT com auto-discovery (substitui REST API e WebSocket)
- **Execução**: Máquina externa, cron diário
- **Estado**: Arquivo state.json para rastrear última leitura e buscar apenas novas
- **Histórico**: Parâmetro --since para baixar dados históricos desde uma data específica e popular state.json. HA recebe a última leitura via MQTT e constrói histórico naturalmente com o recorder
- **MQTT auto-discovery**: Publica config em `homeassistant/sensor/<id>/config` com retain=True. HA cria sensores automaticamente
- **Sensores**: `sensor.aqdata_water_reading` (total_increasing, m³) e `sensor.aqdata_water_consumption` (measurement, m³)

## Notes
- Site usa Adianti Framework: rotas via engine.php?class=X&method=Y
- Login via `loginMorador` (campos: login, senha). Cookie: `PHPSESSID_aqdata`
- Dados em `diario_iot&method=onShow` com params medidor_id, periodo_diario_inicio/fim (DD/MM/YYYY)
- HTML table: Data (DD/MM/YYYY HH:MM:SS), Acumulador (m³), Consumo (m³). Decimais com vírgula
- Medidor ID: 7545 (configurável via .env)
- MQTT não requer long-lived access token — usa user/password do broker
- MQTT retain=True garante que HA recebe o último valor mesmo se reiniciar

## Explore
### Tasks

### Completed
- [x] Pesquisa inicial do site AqData (framework, login, ausência de API REST)
- [x] Definição da abordagem: Script Python + cron + MQTT
- [x] Brainstorming com usuário: login sem 2FA, dados disponíveis, abordagem preferida
- [x] Design aprovado: scraping + state.json + --since para histórico
- [x] Descoberta interativa de endpoints via DevTools com o usuário
- [x] Teste dry-run com credenciais reais: login OK, 8 leituras parseadas corretamente
- [x] Decisão de migrar REST API → MQTT (mais simples, sem token, sem admin)

## Plan
### Tasks

### Architecture
```
hassAqdataWaterSensor/
├── aqdata_scraper.py      # Entry point + CLI args + orquestração
├── aqdata/
│   ├── __init__.py
│   ├── config.py           # Leitura .env + defaults (MQTT settings)
│   ├── auth.py             # Login no site AqData (requests.Session)
│   ├── scraper.py          # Navegação + extração de dados do HTML
│   ├── state.py            # Leitura/escrita state.json
│   └── mqtt.py             # Publicação via MQTT + auto-discovery
├── state.json              # Estado incremental (gitignored)
├── .env                    # Credenciais (gitignored)
├── .env.example            # Template de configuração
├── requirements.txt        # requests, beautifulsoup4, python-dotenv, paho-mqtt
└── .gitignore
```

### Data Flow
```
1. Ler config (.env + CLI args)
2. Carregar state.json (se existir)
3. Login no AqData → obter session cookies
4. Se --since: buscar leituras desde aquela data
   Se não: buscar leituras após state.last_reading_date (ou só a mais recente)
5. Parsear HTML → lista de {date, reading, consumption}
6. Publicar última leitura via MQTT (auto-discovery + state)
7. Atualizar state.json com última data/valor processado
```

### Sensores HA (via MQTT auto-discovery)
| Entity ID | state_class | Descrição | Unidade |
|-----------|-------------|-----------|---------|
| sensor.aqdata_water_reading | total_increasing | Leitura atual do hidrômetro | m³ |
| sensor.aqdata_water_consumption | measurement | Consumo no período | m³ |

Ambos no mesmo device "AqData Hidrômetro" para agrupamento no HA.

### MQTT Topics
| Topic | Conteúdo | Retain |
|-------|----------|--------|
| `homeassistant/sensor/aqdata_water_reading/config` | Auto-discovery config JSON | Sim |
| `homeassistant/sensor/aqdata_water_reading/state` | Valor do totalizador (ex: "823.450") | Sim |
| `homeassistant/sensor/aqdata_water_consumption/config` | Auto-discovery config JSON | Sim |
| `homeassistant/sensor/aqdata_water_consumption/state` | Valor do consumo (ex: "0.450") | Sim |

### CLI
```
python aqdata_scraper.py              # Busca leituras novas (incremental)
python aqdata_scraper.py --since 2024-01-01  # Busca desde data específica
python aqdata_scraper.py --dry-run    # Executa sem enviar ao MQTT
```

### Configuração (.env)
```
AQDATA_BASE_URL=https://sistema.aqdata.com.br
AQDATA_USER=xxx
AQDATA_PASSWORD=xxx
AQDATA_MEDIDOR_ID=7545
MQTT_HOST=192.168.1.100
MQTT_PORT=1883
MQTT_USER=homeassistant
MQTT_PASSWORD=xxx
```

### Error Handling
- Login falha: log erro + exit 1
- Parse falha: log erro + exit 1
- MQTT indisponível: retry 3x com backoff + exit 1
- state.json corrompido: log warning, buscar todas as leituras disponíveis

### Completed

## Code
### Tasks
- [ ] Atualizar config.py: substituir HA_URL/HA_TOKEN por MQTT_HOST/PORT/USER/PASSWORD
- [ ] Criar mqtt.py: publicação MQTT com auto-discovery
- [ ] Atualizar aqdata_scraper.py: usar mqtt.py no lugar de homeassistant.py e statistics.py
- [ ] Atualizar .env.example e requirements.txt
- [ ] Remover homeassistant.py e statistics.py

### Completed
- [x] Criar estrutura do projeto: requirements.txt, .env.example, .gitignore
- [x] Implementar auth.py: login no AqData
- [x] Implementar scraper.py: navegação e extração de dados
- [x] Implementar state.py: leitura/escrita do state.json
- [x] Teste dry-run com credenciais reais

## Commit
### Tasks
- [ ] Commit com migração MQTT completa

### Completed
*None yet*



---
*This plan is maintained by the LLM. Tool responses provide guidance on which phase to focus on and what tasks to work on.*
