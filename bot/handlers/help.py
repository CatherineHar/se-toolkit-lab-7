"""Handler for /help command."""

from .base import HandlerResponse


async def handle_help(text: str = "/help") -> HandlerResponse:
    """
    Handle the /help command.

    Args:
        text: The command text (ignored for /help)

    Returns:
        HandlerResponse with list of available commands
    """
    return HandlerResponse(
        success=True,
        message=(
            "📚 Available Commands:\n\n"
            "/start - Welcome message and bot introduction\n"
            "/help - Show this help message\n"
            "/health - Check backend service status\n"
            "/scores <lab> - Get your scores for a specific lab\n"
            "/labs - List all available labs\n\n"
            "You can also ask questions in natural language:\n"
            "• 'what labs are available?'\n"
            "• 'show my scores for lab-01'\n"
            "• 'how do I submit a lab?'"
        ),
    )
