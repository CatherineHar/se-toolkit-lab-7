"""LMS API client for backend communication."""

import httpx
from typing import Any


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """
        Initialize the LMS client.

        Args:
            base_url: Base URL of the LMS backend (e.g., http://localhost:42002)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """
        Make a GET request to the backend.

        Args:
            endpoint: API endpoint (e.g., "/items/", "/analytics/pass-rates")
            params: Optional query parameters

        Returns:
            Parsed JSON response

        Raises:
            httpx.HTTPError: On HTTP errors
            httpx.ConnectError: On connection errors
        """
        client = await self._get_client()
        url = f"{self.base_url}{endpoint}"
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict[str, Any]:
        """
        Check backend health by calling /items/ endpoint.

        Returns:
            Dict with 'healthy' bool and 'message' str

        Raises:
            httpx.HTTPError: On HTTP errors
            httpx.ConnectError: On connection errors
        """
        try:
            items = await self.get("/items/")
            count = len(items) if isinstance(items, list) else 0
            return {
                "healthy": True,
                "message": f"Backend is healthy. {count} items available.",
                "item_count": count,
            }
        except httpx.ConnectError as e:
            return {
                "healthy": False,
                "message": f"Backend error: connection refused ({self.base_url}). Check that the services are running.",
                "error": str(e),
            }
        except httpx.HTTPStatusError as e:
            return {
                "healthy": False,
                "message": f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.",
                "error": str(e),
            }
        except httpx.HTTPError as e:
            return {
                "healthy": False,
                "message": f"Backend error: {str(e)}. Check the backend configuration.",
                "error": str(e),
            }

    async def get_labs(self) -> list[dict[str, Any]]:
        """
        Get list of available labs.

        Returns:
            List of lab dictionaries with 'id', 'name', 'type' keys

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        items = await self.get("/items/")
        if not isinstance(items, list):
            return []

        # Filter for labs (type may vary based on backend implementation)
        labs = []
        for item in items:
            if isinstance(item, dict):
                labs.append(item)
        return labs

    async def get_pass_rates(self, lab: str) -> dict[str, Any]:
        """
        Get pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            Dict with pass rate data per task

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        return await self.get("/analytics/pass-rates", params={"lab": lab})
