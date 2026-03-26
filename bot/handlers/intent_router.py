"""Intent router for natural language message handling."""

from services.llm_client import LLMClient, get_tool_definitions

from .base import HandlerResponse

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You help students and instructors get information about labs, scores, pass rates, and learners.

You have access to tools that fetch data from the backend API. Use these tools to answer questions.

When answering:
- Be concise but informative
- Use specific numbers when available (percentages, counts)
- If data is missing or empty, say so clearly
- If you can't answer with the available tools, say "I can't help with that" and suggest what you CAN do

Available capabilities:
- List available labs and tasks
- Show pass rates and scores for specific labs
- Show top learners, group performance, completion rates
- Show submission timelines
- Trigger data sync

Always use the tools to get real data before answering questions about specific labs or scores."""


async def handle_natural_language(message: str) -> HandlerResponse:
    """
    Handle natural language messages using LLM intent routing.

    Args:
        message: The user's message in natural language

    Returns:
        HandlerResponse with the LLM's answer
    """
    from config import load_config

    config = load_config(test_mode=True)

    # Check if we have LLM configuration
    if not config.llm_api_key or not config.llm_api_base_url:
        # Fallback: suggest using slash commands
        return HandlerResponse(
            success=True,
            message=(
                "I can help you with:\n"
                "• /start - Welcome message\n"
                "• /help - Available commands\n"
                "• /health - Backend status\n"
                "• /labs - List all labs\n"
                "• /scores <lab> - View scores for a lab\n\n"
                "To enable natural language queries, configure the LLM API."
            ),
        )

    llm_client = LLMClient(
        config.llm_api_base_url,
        config.llm_api_key,
        config.llm_api_model if hasattr(config, "llm_api_model") else "coder-model",
    )

    try:
        tools = get_tool_definitions()

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        response = await llm_client.chat_with_tools(messages, tools)

        return HandlerResponse(
            success=True,
            message=response,
        )
    except Exception as e:
        error_msg = str(e)
        return HandlerResponse(
            success=False,
            message=f"Error processing your request: {error_msg}\n\nTry using a slash command like /help or /labs.",
        )
    finally:
        await llm_client.close()
