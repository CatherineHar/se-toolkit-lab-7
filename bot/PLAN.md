# Bot Development Plan

## Overview

This document outlines the development approach for the LMS Telegram Bot, which serves as an interface between students and the Learning Management System. The bot provides command-based access to lab information, scores, and general assistance through Telegram.

## Architecture Principles

### 1. Testable Handler Architecture (P0.1)

The core principle is **separation of concerns**: handlers contain pure business logic without any Telegram-specific dependencies. This means:

- Handlers are simple functions that take input (command string, user context) and return output (text, structured data)
- No Telegram imports or dependencies in handler code
- The same handler functions work in both test mode (`--test`) and production mode (Telegram)
- Testing requires no network connection or Telegram bot token

### 2. CLI Test Mode (P0.2)

The `--test` flag enables offline verification:

```bash
cd bot
uv run bot.py --test "/start"                    # Prints welcome message to stdout
uv run bot.py --test "/help"                     # Prints available commands
uv run bot.py --test "/health"                   # Checks backend connectivity
uv run bot.py --test "/scores lab-04"            # Fetches lab scores
uv run bot.py --test "what labs are available"   # Natural language query
```

The test mode:
- Reads configuration from `.env.bot.secret`
- Does NOT connect to Telegram (no `BOT_TOKEN` needed)
- Prints handler response directly to stdout
- Exits with code 0 on success

## Development Phases

### Phase 1: Scaffold (Current Task)

Create the basic project structure:
- `bot/bot.py` - Entry point with `--test` mode support
- `bot/handlers/` - Command handlers (start, help, health)
- `bot/services/` - API client stubs
- `bot/config.py` - Environment variable loading
- `bot/pyproject.toml` - Dependencies

### Phase 2: Backend Integration

Connect handlers to the backend API:
- Implement `LMSClient` service for API communication
- Add authentication with `LMS_API_KEY`
- Implement `/scores` handler to fetch lab scores
- Implement `/labs` handler to list available labs
- Add error handling for network failures and API errors

### Phase 3: Intent Routing

Implement natural language processing:
- Add LLM client service (using `LLM_API_KEY`)
- Create intent classifier to route natural language to handlers
- Handle queries like "what labs are available" → `/labs` handler
- Implement fallback responses for unrecognized intents

### Phase 4: Deployment

Finalize for production:
- Create `.env.bot.secret` with real credentials on VM
- Update Docker configuration if needed
- Test end-to-end with Telegram
- Add logging and monitoring

## File Structure

```
bot/
├── bot.py              # Entry point: argparse for --test, Telegram startup
├── config.py           # Configuration: load env vars, validate required values
├── pyproject.toml      # Dependencies: aiogram, httpx, pydantic-settings
├── PLAN.md             # This file
├── handlers/
│   ├── __init__.py
│   ├── base.py         # Base handler interface
│   ├── start.py        # /start command
│   ├── help.py         # /help command
│   ├── health.py       # /health command
│   └── scores.py       # /scores command (Phase 2)
└── services/
    ├── __init__.py
    ├── lms_client.py   # LMS API client (Phase 2)
    └── llm_client.py   # LLM client for intent routing (Phase 3)
```

## Key Decisions

1. **uv over pip**: Using `uv` for dependency management as per project standards
2. **No requirements.txt**: Dependencies defined in `pyproject.toml` only
3. **Handler interface**: All handlers implement a common interface for consistency
4. **Environment files**: `.env.bot.example` for template, `.env.bot.secret` for real values
