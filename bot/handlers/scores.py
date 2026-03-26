"""Handler for /scores command."""

from .base import HandlerResponse


async def handle_scores(text: str = "/scores") -> HandlerResponse:
    """
    Handle the /scores command.

    Args:
        text: The command text (e.g., "/scores lab-04")

    Returns:
        HandlerResponse with scores information
    """
    # Parse lab name from command
    parts = text.split()
    lab_name = parts[1] if len(parts) > 1 else None

    if not lab_name:
        return HandlerResponse(
            success=True,
            message=(
                "📊 Usage: /scores <lab-name>\n\n"
                "Examples:\n"
                "• /scores lab-01\n"
                "• /scores lab-04\n\n"
                "Available labs: lab-01 through lab-07"
            ),
        )

    # TODO: Implement actual scores lookup in Phase 2
    return HandlerResponse(
        success=True,
        message=(
            f"📊 Scores for {lab_name}:\n\n"
            f"Status: Pending\n"
            f"Score: N/A\n\n"
            f"Submit your work to get scored for {lab_name}."
        ),
    )
