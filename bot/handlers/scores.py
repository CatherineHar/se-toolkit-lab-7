"""Handler for /scores command."""

from services.lms_client import LMSClient

from .base import HandlerResponse


async def handle_scores(text: str = "/scores") -> HandlerResponse:
    """
    Handle the /scores command.

    Args:
        text: The command text (e.g., "/scores lab-04")

    Returns:
        HandlerResponse with scores information
    """
    from config import load_config

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
                "Use /labs to see available labs."
            ),
        )

    # Convert lab-01 format to numeric ID if needed
    # Backend accepts both "lab-01" and "1"
    lab_id = lab_name
    if lab_name.lower().startswith("lab-"):
        try:
            lab_id = str(int(lab_name[4:].lstrip("0") or "0"))
        except ValueError:
            pass  # Keep original if not a valid number

    config = load_config(test_mode=True)
    client = LMSClient(config.lms_api_base_url, config.lms_api_key)

    try:
        pass_rates = await client.get_pass_rates(lab_id)

        if not pass_rates:
            return HandlerResponse(
                success=True,
                message=f"No pass rate data available for {lab_name}.",
            )

        # Format pass rates for display
        # API format: [{"task": "Task Name", "avg_score": 85.3, "attempts": 2754}, ...]
        lines = [f"Pass rates for {lab_name}:"]

        if isinstance(pass_rates, list):
            for item in pass_rates:
                if isinstance(item, dict):
                    task = item.get("task", "Unknown Task")
                    # avg_score is already a percentage (0-100)
                    avg_score = item.get("avg_score", 0)
                    attempts = item.get("attempts", 0)

                    lines.append(f"- {task}: {avg_score:.1f}% ({attempts} attempts)")
        elif isinstance(pass_rates, dict):
            # Handle dict format if backend returns differently
            for task, data in pass_rates.items():
                if isinstance(data, dict):
                    avg_score = data.get("avg_score", data.get("pass_rate", 0))
                    attempts = data.get("attempts", data.get("total_attempts", 0))
                    lines.append(f"- {task}: {avg_score:.1f}% ({attempts} attempts)")

        return HandlerResponse(
            success=True,
            message="\n".join(lines),
        )
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "Not Found" in error_msg:
            return HandlerResponse(
                success=False,
                message=f"No data found for {lab_name}. Check the lab name with /labs.",
            )
        return HandlerResponse(
            success=False,
            message=f"Error fetching scores: {error_msg}",
        )
    finally:
        await client.close()
