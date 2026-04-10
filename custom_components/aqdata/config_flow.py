"""Config flow for AqData integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_MEDIDOR_ID, DOMAIN
from .scraper import AqDataScraper

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_MEDIDOR_ID): str,
    }
)


class AqDataConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AqData."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            scraper = AqDataScraper(
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
                medidor_id=user_input[CONF_MEDIDOR_ID],
            )

            try:
                valid = await self.hass.async_add_executor_job(scraper.login)
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception during login")
                errors["base"] = "cannot_connect"
            else:
                if valid:
                    await self.async_set_unique_id(user_input[CONF_USERNAME])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"AqData ({user_input[CONF_USERNAME]})",
                        data=user_input,
                    )
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
