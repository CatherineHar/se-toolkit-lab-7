#!/usr/bin/env python3
"""Debug script to check config loading."""
from config import load_config, ENV_FILE

print(f"ENV_FILE path: {ENV_FILE}")

cfg = load_config(test_mode=False)
print(f"bot_token loaded: {cfg.bot_token[:10] if cfg.bot_token else 'None'}")
print(f"lms_api_key loaded: {cfg.lms_api_key}")
