"""TeslaFi API Client"""

from json import JSONDecodeError
import httpx
import logging

from .model import TeslaFiVehicle

REQUEST_TIMEOUT = 5
_LOGGER = logging.getLogger(__name__)


class TeslaFiClient:
    """TeslaFi API Client"""

    _api_key: str
    _client: httpx.AsyncClient

    def __init__(
        self,
        api_key: str,
        client: httpx.AsyncClient,
    ) -> None:
        """
        Creates a new TeslaFi API Client.

        :param api_key: API Key can be obtained from https://www.teslafi.com/api.php
        """
        self._api_key = api_key
        self._client = client

    async def last_good(self) -> TeslaFiVehicle:
        """
        Return last data point with charge data
        """
        return TeslaFiVehicle(await self._request("lastGood"))

    async def command(self, cmd: str, **kwargs) -> dict:
        """
        Execute a command.
        See list of commands at https://teslafi.com/api.php
        """
        return await self._request(cmd, **kwargs)

    async def _request(self, command: str = "", **kwargs) -> dict:
        """
        :param command: The command to send. Can be empty string, `lastGood`, etc. See
        """
        timeout = kwargs.get("wake", 0) + REQUEST_TIMEOUT
        response = await self._client.get(
            url="https://www.teslafi.com/feed.php",
            headers={"Authorization": "Bearer " + self._api_key},
            params={"command": command} | kwargs,
            timeout=timeout,
        )
        assert response.status_code < 400

        try:
            data = response.json()
        except JSONDecodeError as exc:
            if response.text == "This command is not enabled in the TeslaFi API.":
                raise PermissionError(response.text) from exc
            _LOGGER.warning("Error reading as json: %s", response.text, exc_info=True)
            raise SyntaxError("Failed parsing JSON") from exc

        if isinstance(data, dict):
            if err := data.get("error"):
                raise RuntimeError(f"{err}: {data.get('error_description')}")
            if data.get("response", {}).get("result", None) == "unauthorized":
                raise PermissionError(
                    f"TeslaFi response unauthorized for api key {self._api_key}: {data}"
                )

        return data
