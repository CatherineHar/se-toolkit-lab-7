"""Command handlers for the Telegram bot."""

from .base import HandlerResponse
from .help import handle_help
from .health import handle_health
from .intent_router import handle_natural_language
from .labs import handle_labs
from .scores import handle_scores
from .start import handle_start

__all__ = [
    "HandlerResponse",
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_natural_language",
]
