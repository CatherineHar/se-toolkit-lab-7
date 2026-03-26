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

from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_natural_language,
    handle_scores,
    handle_start,
)


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

    # Check if it's a natural language query (doesn't start with /)
    if not command.startswith("/"):
        response = await handle_natural_language(command)
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

    @dp.callback_query()
    async def handle_callback(callback) -> None:
        """Handle inline keyboard button clicks."""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        data = callback.data
        message = callback.message

        if data == "view_labs":
            response = await handle_labs("/labs")
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 Back",
                            callback_data="back",
                        ),
                    ],
                ],
            )
            await message.edit_text(response.message, reply_markup=keyboard)
        elif data == "health_check":
            response = await handle_health("/health")
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 Back",
                            callback_data="back",
                        ),
                    ],
                ],
            )
            await message.edit_text(response.message, reply_markup=keyboard)
        elif data == "scores":
            # Prompt for lab name
            await message.answer(
                "Please specify a lab (e.g., 'lab-04') or use /scores <lab> command."
            )
        elif data == "help":
            response = await handle_help("/help")
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 Back",
                            callback_data="back",
                        ),
                    ],
                ],
            )
            await message.edit_text(response.message, reply_markup=keyboard)
        elif data == "back":
            # Show the main menu again
            response = await handle_start("/start")
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📋 View Labs",
                            callback_data="view_labs",
                        ),
                        InlineKeyboardButton(
                            text="🏥 Health Check",
                            callback_data="health_check",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="📊 My Scores",
                            callback_data="scores",
                        ),
                        InlineKeyboardButton(
                            text="❓ Help",
                            callback_data="help",
                        ),
                    ],
                ],
            )
            await message.edit_text(response.message, reply_markup=keyboard)

        await callback.answer()

    @dp.message()
    async def handle_message(message: Message) -> None:
        """Handle incoming Telegram messages."""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        text = message.text or ""

        # Route to appropriate handler
        if text.startswith("/start"):
            response = await handle_start(text)
            # Add inline keyboard buttons for common actions
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📋 View Labs",
                            callback_data="view_labs",
                        ),
                        InlineKeyboardButton(
                            text="🏥 Health Check",
                            callback_data="health_check",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="📊 My Scores",
                            callback_data="scores",
                        ),
                        InlineKeyboardButton(
                            text="❓ Help",
                            callback_data="help",
                        ),
                    ],
                ],
            )
            await message.answer(response.message, reply_markup=keyboard)
        elif text.startswith("/help"):
            response = await handle_help(text)
            await message.answer(response.message)
        elif text.startswith("/health"):
            response = await handle_health(text)
            await message.answer(response.message)
        elif text.startswith("/labs"):
            response = await handle_labs(text)
            await message.answer(response.message)
        elif text.startswith("/scores"):
            response = await handle_scores(text)
            await message.answer(response.message)
        elif text.startswith("/"):
            # Unknown slash command
            await message.answer(
                f"Unknown command: {text}\n\nUse /help to see available commands."
            )
        else:
            # Natural language message - use intent router
            response = await handle_natural_language(text)
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
