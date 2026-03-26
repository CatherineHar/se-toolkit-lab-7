"""Handler for /health command."""

from .base import HandlerResponse


async def handle_health(text: str = "/health") -> HandlerResponse:
    """
    Handle the /health command.

    Args:
        text: The command text (ignored for /health)

    Returns:
        HandlerResponse with backend health status
    """
    # TODO: Implement actual backend health check in Phase 2
    return HandlerResponse(
        success=True,
        message=(
            "🏥 Service Status:\n\n"
            "• Backend: OK\n"
            "• Database: OK\n"
            "• Bot: OK\n\n"
            "All systems operational."
        ),
    )
