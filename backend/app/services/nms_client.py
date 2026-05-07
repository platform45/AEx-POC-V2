import httpx
from typing import Any


class NMSClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get_device_status(self, device_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/devices/{device_id}/status")
            response.raise_for_status()
            return response.json()

    async def run_diagnostic(self, device_id: str, command: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/devices/{device_id}/diagnostics",
                json={"command": command},
            )
            response.raise_for_status()
            return response.json()
