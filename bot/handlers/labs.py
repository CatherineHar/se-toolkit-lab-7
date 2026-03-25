"""Handler for /labs command."""

from .base import HandlerResponse


async def handle_labs(text: str = "/labs") -> HandlerResponse:
    """
    Handle the /labs command.

    Args:
        text: The command text (ignored for /labs)

    Returns:
        HandlerResponse with list of available labs
    """
    return HandlerResponse(
        success=True,
        message=(
            "📋 Available Labs:\n\n"
            "• lab-01 - Market & Product\n"
            "• lab-02 - Git & Version Control\n"
            "• lab-03 - Docker & Containerization\n"
            "• lab-04 - Testing & CI/CD\n"
            "• lab-05 - Database Design\n"
            "• lab-06 - API Development\n"
            "• lab-07 - Full Stack Integration\n\n"
            "Use /scores <lab-name> to check your scores."
        ),
    )
