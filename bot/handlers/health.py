"""Handler for /health command."""

from services.lms_client import LMSClient

from .base import HandlerResponse


async def handle_health(text: str = "/health") -> HandlerResponse:
    """
    Handle the /health command.

    Args:
        text: The command text (ignored for /health)

    Returns:
        HandlerResponse with backend health status
    """
    from config import load_config

    config = load_config(test_mode=True)
    client = LMSClient(config.lms_api_base_url, config.lms_api_key)

    try:
        result = await client.health_check()
        return HandlerResponse(
            success=result["healthy"],
            message=result["message"],
        )
    finally:
        await client.close()
