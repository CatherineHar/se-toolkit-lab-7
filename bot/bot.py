#!/usr/bin/env python3
"""
LMS Telegram Bot Entry Point.

Usage:
    Telegram mode:  python bot.py
    Test mode:      python bot.py --test "/command"
"""

import argparse
import asyncio
import sys

from config import load_config, validate_config

from handlers import handle_help, handle_health, handle_labs, handle_scores, handle_start


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
    )
    parser.add_argument(
        "--test",
        type=str,
        nargs="?",
        const="",
        metavar="COMMAND",
        help="Run in test mode with optional command (e.g., '/start')",
    )
    return parser.parse_args()


async def run_test_mode(command: str) -> int:
    """
    Run bot in test mode - call handlers directly without Telegram.

    Args:
        command: The command to test (e.g., "/start", "/help")

    Returns:
        Exit code (0 for success, 1 for error)
    """
    config = load_config(test_mode=True)

    # Validate config for test mode (less strict)
    errors = validate_config(config, test_mode=True)
    if errors:
        print(f"Configuration errors: {errors}", file=sys.stderr)
        return 1

    # Route command to appropriate handler
    command = command.strip() if command else "/start"

    handler_map = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": handle_scores,
    }

    # Check for exact command match
    if command in handler_map:
        response = await handler_map[command](command)
        print(response.message)
        return 0 if response.success else 1

    # Handle commands with arguments (e.g., "/scores lab-04")
    cmd_parts = command.split()
    if cmd_parts and cmd_parts[0] in handler_map:
        response = await handler_map[cmd_parts[0]](command)
        print(response.message)
        return 0 if response.success else 1

    # Unknown command - show help
    print(f"Unknown command: {command}")
    print("\nTry these commands:")
    print("  /start  - Welcome message")
    print("  /help   - Show available commands")
    print("  /health - Check service status")
    return 0


async def run_telegram_mode() -> int:
    """
    Run bot in Telegram mode.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.types import Message
    except ImportError:
        print("aiogram not installed. Run: uv sync", file=sys.stderr)
        return 1

    config = load_config(test_mode=False)

    # Validate config for Telegram mode
    errors = validate_config(config, test_mode=False)
    if errors:
        print(f"Configuration errors: {errors}", file=sys.stderr)
        return 1

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    @dp.message()
    async def handle_message(message: Message) -> None:
        """Handle incoming Telegram messages."""
        text = message.text or ""

        # Route to appropriate handler
        if text.startswith("/start"):
            response = await handle_start(text)
        elif text.startswith("/help"):
            response = await handle_help(text)
        elif text.startswith("/health"):
            response = await handle_health(text)
        elif text.startswith("/labs"):
            response = await handle_labs(text)
        elif text.startswith("/scores"):
            response = await handle_scores(text)
        else:
            response = await handle_help(text)

        await message.answer(response.message)

    print("Starting bot in Telegram mode...")
    await dp.start_polling(bot)
    return 0


async def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.test is not None:
        # Test mode: run command and exit
        command = args.test if args.test else "/start"
        return await run_test_mode(command)
    else:
        # Telegram mode: start polling
        return await run_telegram_mode()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
