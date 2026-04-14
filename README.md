# AqData Water Meter - Home Assistant Integration

Custom integration for [AqData](https://sistema.aqdata.com.br) water meters (hidrômetros). Fetches water consumption data from the AqData cloud platform and exposes it as Home Assistant sensors.

## Sensors

| Sensor | Description | State Class |
|--------|-------------|-------------|
| Leitura (Reading) | Absolute meter totalizer (m³) | TOTAL_INCREASING |
| Consumo (Consumption) | Consumption since last reading (m³) | MEASUREMENT |

Both sensors use `device_class: water` and are compatible with the Home Assistant Energy/Water dashboard.

Data is refreshed every 4 hours via `DataUpdateCoordinator`.

## Installation

### HACS (recommended)

1. In HACS, go to **Integrations** → menu (⋮) → **Custom repositories**
2. Add this repository URL and select category **Integration**
3. Search for "AqData Water Meter" and install
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/aqdata/` directory to `/config/custom_components/aqdata/`
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "AqData"
3. Enter your AqData credentials:
   - **Usuário** — AqData login username
   - **Senha** — AqData login password
   - **ID do Medidor** — Your water meter ID (found in the AqData web portal)

## Requirements

- Home Assistant >= 2024.1
- `beautifulsoup4 >= 4.12`
