import logging
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class Reading:
    date: datetime
    totalizer: float  # Acumulador (m³) — absolute meter reading
    consumption: float  # Consumo (m³) — consumption since last reading


def fetch_readings(
    session: requests.Session,
    base_url: str,
    medidor_id: str,
    start_date: datetime,
    end_date: datetime,
) -> list[Reading]:
    """Fetch daily readings from AqData for the given date range."""
    url = f"{base_url}/engine.php"
    params = {
        "class": "diario_iot",
        "method": "onShow",
        "medidor_id": medidor_id,
        "medidor": medidor_id,
        "periodo_diario_inicio": start_date.strftime("%d/%m/%Y"),
        "periodo_diario_fim": end_date.strftime("%d/%m/%Y"),
        "current_tab_abas_morador": "2",
    }

    logger.info("Fetching readings from %s to %s", start_date.date(), end_date.date())
    resp = session.get(url, params=params)
    resp.raise_for_status()

    return _parse_readings(resp.text)


def _parse_readings(html: str) -> list[Reading]:
    """Parse the HTML table of readings from the diario_iot page."""
    soup = BeautifulSoup(html, "html.parser")
    readings: list[Reading] = []

    for tr in soup.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 7:
            continue

        # Skip empty rows (contain &nbsp;)
        date_text = cells[4].get_text(strip=True)
        if not date_text or date_text == "\xa0":
            continue

        try:
            reading_date = datetime.strptime(date_text, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            logger.debug("Skipping row with unparsable date: %s", date_text)
            continue

        totalizer = _parse_brazilian_number(cells[5].get_text(strip=True))
        consumption = _parse_brazilian_number(cells[6].get_text(strip=True))

        readings.append(Reading(
            date=reading_date,
            totalizer=totalizer,
            consumption=consumption,
        ))

    logger.info("Parsed %d readings", len(readings))
    return readings


def _parse_brazilian_number(text: str) -> float:
    """Parse a Brazilian-formatted number like '823,450' or '0,000'."""
    if not text or text == "\xa0":
        return 0.0
    return float(text.replace(".", "").replace(",", "."))
