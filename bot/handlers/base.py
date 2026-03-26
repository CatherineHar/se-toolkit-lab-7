"""Base handler interface and types."""

from dataclasses import dataclass


@dataclass
class HandlerResponse:
    """Standard response from a handler."""

    success: bool
    message: str
    data: dict | None = None


class BaseHandler:
    """Base class for all handlers."""

    async def handle(self, text: str) -> HandlerResponse:
        """
        Handle the command and return a response.

        Args:
            text: The command text (e.g., "/start" or "what labs are available")

        Returns:
            HandlerResponse with success status and message
        """
        raise NotImplementedError
