"""AqData scraper — login + fetch latest reading.

Reuses logic from aqdata/auth.py and aqdata/scraper.py.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from .const import DEFAULT_BASE_URL

_LOGGER = logging.getLogger(__name__)


class AqDataScraper:
    """Scrapes water meter readings from the AqData portal."""

    def __init__(
        self,
        username: str,
        password: str,
        medidor_id: str,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self._username = username
        self._password = password
        self._medidor_id = medidor_id
        self._base_url = base_url
        self._session = requests.Session()

    def login(self) -> bool:
        """Log in to AqData. Returns True on success."""
        url = f"{self._base_url}/engine.php"
        params = {"class": "loginMorador", "method": "onLogin"}
        data = {"login": self._username, "senha": self._password}

        _LOGGER.info("Logging in as %s", self._username)
        resp = self._session.post(url, params=params, data=data)
        resp.raise_for_status()

        if "MoradorPaginaExterna" in resp.text:
            _LOGGER.info("Login successful")
            return True

        if "__adianti_error" in resp.text:
            _LOGGER.error("Login failed: server returned error")
            return False

        _LOGGER.error("Login failed: unexpected response")
        return False

    def fetch_latest(self) -> dict[str, float | str]:
        """Fetch the most recent reading.

        Returns dict with keys: totalizer (float, m³), consumption (float, m³), date (str).
        Raises RuntimeError if no readings found.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        url = f"{self._base_url}/engine.php"
        params = {
            "class": "diario_iot",
            "method": "onShow",
            "medidor_id": self._medidor_id,
            "medidor": self._medidor_id,
            "periodo_diario_inicio": start_date.strftime("%d/%m/%Y"),
            "periodo_diario_fim": end_date.strftime("%d/%m/%Y"),
            "current_tab_abas_morador": "2",
        }

        _LOGGER.info("Fetching readings for medidor %s", self._medidor_id)
        resp = self._session.get(url, params=params)
        resp.raise_for_status()

        readings = self._parse_readings(resp.text)
        if not readings:
            raise RuntimeError("No readings found")

        latest = readings[-1]
        return {
            "totalizer": latest["totalizer"],
            "consumption": latest["consumption"],
            "date": latest["date"],
        }

    @staticmethod
    def _parse_readings(html: str) -> list[dict]:
        """Parse the HTML table of readings."""
        soup = BeautifulSoup(html, "html.parser")
        readings: list[dict] = []

        for tr in soup.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) < 7:
                continue

            date_text = cells[4].get_text(strip=True)
            if not date_text or date_text == "\xa0":
                continue

            try:
                parsed_date = datetime.strptime(date_text, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                _LOGGER.debug("Skipping row with unparsable date: %s", date_text)
                continue

            totalizer = _parse_brazilian_number(cells[5].get_text(strip=True))
            consumption = _parse_brazilian_number(cells[6].get_text(strip=True))

            readings.append({
                "date": parsed_date.isoformat(),
                "totalizer": totalizer,
                "consumption": consumption,
            })

        _LOGGER.info("Parsed %d readings", len(readings))
        return readings


def _parse_brazilian_number(text: str) -> float:
    """Parse a Brazilian-formatted number like '823,450' or '0,000'."""
    if not text or text == "\xa0":
        return 0.0
    return float(text.replace(".", "").replace(",", "."))
