"""Handler for /labs command."""

from services.lms_client import LMSClient

from .base import HandlerResponse


async def handle_labs(text: str = "/labs") -> HandlerResponse:
    """
    Handle the /labs command.

    Args:
        text: The command text (ignored for /labs)

    Returns:
        HandlerResponse with list of available labs
    """
    from config import load_config

    config = load_config(test_mode=True)
    client = LMSClient(config.lms_api_base_url, config.lms_api_key)

    try:
        items = await client.get_labs()

        if not items:
            return HandlerResponse(
                success=True,
                message="No labs available at the moment.",
            )

        # Filter for labs only (not tasks)
        labs = [item for item in items if isinstance(item, dict) and item.get("type") == "lab"]

        if not labs:
            return HandlerResponse(
                success=True,
                message="No labs available at the moment.",
            )

        # Format labs for display
        # API format: {"type": "lab", "title": "Lab 01 – Products, Architecture & Roles", "id": 1, ...}
        lab_lines = []
        for lab in labs:
            title = lab.get("title", "Unknown Lab")
            lab_lines.append(f"- {title}")

        return HandlerResponse(
            success=True,
            message="Available labs:\n" + "\n".join(lab_lines),
        )
    except Exception as e:
        return HandlerResponse(
            success=False,
            message=f"Error fetching labs: {str(e)}",
        )
    finally:
        await client.close()
