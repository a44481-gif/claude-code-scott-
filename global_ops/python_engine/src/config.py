"""
GlobalOPS · 配置加载模块
支持 .env 和 YAML 配置
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import yaml

BASE_DIR = Path(__file__).parent.parent.parent  # global_ops/
ENV_FILE = BASE_DIR / "config" / ".env"
PLATFORMS_FILE = BASE_DIR / "config" / "platforms.yaml"

load_dotenv(ENV_FILE)


def get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def get_platforms_config() -> dict:
    if not PLATFORMS_FILE.exists():
        return {}
    with open(PLATFORMS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_db_config() -> dict:
    return {
        "host": get_env("POSTGRES_HOST", "localhost"),
        "port": get_env("POSTGRES_PORT", "5432"),
        "dbname": get_env("POSTGRES_DB", "global_ops"),
        "user": get_env("POSTGRES_USER", "postgres"),
        "password": get_env("POSTGRES_PASSWORD", ""),
    }


def get_ai_config() -> dict:
    return {
        "anthropic_api_key": get_env("ANTHROPIC_API_KEY", ""),
        "deepl_api_key": get_env("DEEPL_API_KEY", ""),
        "openai_api_key": get_env("OPENAI_API_KEY", ""),
    }


PLATFORMS = get_platforms_config()
DB_CONFIG = get_db_config()
AI_CONFIG = get_ai_config()
