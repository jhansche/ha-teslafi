"""Config flow for Bird Buddy integration."""
from __future__ import annotations

from typing import Any
import httpx

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.httpx_client import get_async_client

from .client import TeslaFiClient
from .const import DOMAIN

STEP_AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bird Buddy."""

    _client: TeslaFiClient | None

    VERSION = 2

    def __init__(self) -> None:
        self._client = None
        super().__init__()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_AUTH_SCHEMA)

        errors = {}
        if user_input is not None:
            result = await self._async_auth_or_validate(user_input, errors)
            if result is not None:
                await self.async_set_unique_id(result["id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=result["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_AUTH_SCHEMA,
            errors=errors,
        )

    async def _async_auth_or_validate(self, user_input, errors):
        http_client = get_async_client(self.hass)
        self._client = TeslaFiClient(user_input[CONF_API_KEY], http_client)
        try:
            result = await self._client.last_good()
        except httpx.HTTPStatusError as ex:
            self._client = None
            if ex.response.status_code == 403:
                errors["base"] = "invalid_auth"
            else:
                errors["base"] = "cannot_connect"
            return None
        except httpx.RequestError:
            self._client = None
            errors["base"] = "cannot_connect"
            return None
        if not result:
            self._client = None
            errors["base"] = "cannot_connect"
            return None
        return {
            "title": result.name,
            "id": result.id,
        }
