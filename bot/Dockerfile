# Bot Dockerfile
# Uses uv for dependency management (no requirements.txt)

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

# Set working directory
WORKDIR /app

# Copy bot project files
COPY bot/pyproject.toml ./

# Install dependencies using uv
RUN uv sync --no-dev

# Copy bot source code
COPY bot/ ./bot/

# Copy root .env.bot.secret for configuration
COPY .env.bot.secret ./.env.bot.secret

# Set environment variables
ENV PYTHONPATH=/app
ENV BOT_ROOT=/app

# Run the bot
CMD ["uv", "run", "python", "bot/bot.py"]
