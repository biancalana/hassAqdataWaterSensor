# Development Plan: hassAqdataWaterSensor (main branch)

*Generated on 2026-04-10 by Vibe Feature MCP*
*Workflow: [epcc](https://mrsimpson.github.io/responsible-vibe-mcp/workflows/epcc)*

## Goal
Script Python que faz scraping do site AqData (sistema.aqdata.com.br) para obter leituras diárias do hidrômetro e envia os dados para o Home Assistant via MQTT + WebSocket statistics import.

## Key Decisions
- **Abordagem**: Script Python + cron (não custom HACS integration)
- **Scraping**: Site AqData é PHP/Adianti Framework. Login via `loginMorador`, dados em `diario_iot&method=onShow`
- **Envio diário**: MQTT com auto-discovery (paho-mqtt)
- **Histórico (--since)**: WebSocket statistics import (external statistics, source: "aqdata")
- **Sensores MQTT**: `sensor.aqdata_water_reading` (total_increasing) e `sensor.aqdata_water_consumption` (measurement)
- **External statistics**: `aqdata:water_total` e `aqdata:water_consumption` (Water Dashboard)

## Notes
- Login: campos `login` e `senha`, cookie `PHPSESSID_aqdata`
- Dados: tabela HTML com Data, Acumulador (m³), Consumo (m³). Decimais com vírgula
- Medidor ID: 7545 (configurável via .env)
- MQTT: retain=True, auto-discovery no tópico `homeassistant/sensor/<id>/config`
- Statistics: timestamps alinhados por hora, timezone-aware

## Explore
### Tasks

### Completed
- [x] Pesquisa do site AqData, descoberta de endpoints via DevTools
- [x] Design aprovado: scraping + MQTT + statistics import
- [x] Teste dry-run e teste real com credenciais AqData
- [x] MQTT publishing funcional
- [x] WebSocket statistics import funcional (Water Dashboard)

## Plan
### Tasks
- [ ] Decidir: rodar como pyscript dentro do HA ou manter externo com cron
- [ ] Se pyscript: migrar script para formato pyscript (elimina MQTT/WebSocket deps)
- [ ] Se externo: configurar cron e documentar setup

### Completed
*None yet*

## Code
### Tasks
- [ ] Migrar para o formato escolhido (pyscript ou cron externo)
- [ ] Limpar código de diagnóstico
- [ ] Commit final

### Completed
- [x] Scraper AqData funcional (login + parse HTML)
- [x] MQTT com auto-discovery funcional
- [x] WebSocket statistics import funcional
- [x] state.json para tracking incremental
- [x] CLI com --since e --dry-run

## Commit
### Tasks
- [ ] Commit da decisão final (pyscript ou setup cron)

### Completed
- [x] Commit inicial: scraper + MQTT
- [x] Commit: historical data import via WebSocket
