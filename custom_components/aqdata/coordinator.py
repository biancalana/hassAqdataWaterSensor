"""DataUpdateCoordinator for AqData integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_MEDIDOR_ID, DOMAIN
from .scraper import AqDataScraper

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(hours=4)


class AqDataCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator to fetch AqData water meter readings."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self._scraper = AqDataScraper(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            medidor_id=entry.data[CONF_MEDIDOR_ID],
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from AqData."""
        try:
            data = await self.hass.async_add_executor_job(self._fetch)
        except ConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except AuthError as err:
            raise ConfigEntryAuthFailed(f"Auth failed: {err}") from err
        return data

    def _fetch(self) -> dict:
        """Synchronous fetch: login then get latest reading."""
        if not self._scraper.login():
            raise AuthError("Login failed — check credentials")
        return self._scraper.fetch_latest()


class AuthError(Exception):
    """Raised when login fails."""
