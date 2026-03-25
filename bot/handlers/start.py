"""Handler for /start command."""

from .base import HandlerResponse


async def handle_start(text: str = "/start") -> HandlerResponse:
    """
    Handle the /start command.

    Args:
        text: The command text (ignored for /start)

    Returns:
        HandlerResponse with welcome message
    """
    return HandlerResponse(
        success=True,
        message=(
            "👋 Welcome to the LMS Telegram Bot!\n\n"
            "I can help you with:\n"
            "• Checking your lab scores\n"
            "• Viewing available labs\n"
            "• Getting help with commands\n\n"
            "Use /help to see all available commands."
        ),
    )
