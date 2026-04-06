"""
Config loader with JSON + environment variable override.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


def load_config(
    agent_name: Optional[str] = None,
    config_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Load JSON config file with environment variable overrides.

    Priority: env vars > JSON config > defaults

    Args:
        agent_name: Agent name for constructing default config path
        config_path: Explicit config file path (overrides agent_name)

    Env var format: {AGENT_NAME}_{SECTION}_{KEY} = value
    Example: IT_NEWS_AI_API_KEY = "sk-xxx"
             PC_PARTS_CRAWLING_TIMEOUT = 30
    """
    if config_path:
        base_path = Path(config_path)
    elif agent_name:
        base_path = Path(__file__).parent.parent / agent_name / "config" / "settings.json"
    else:
        return {}

    # Load JSON config
    config: Dict[str, Any] = {}
    if base_path.exists():
        try:
            with open(base_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.info(f"已加载配置: {base_path}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            config = {}
    else:
        logger.warning(f"配置文件不存在: {base_path}")

    # Apply environment variable overrides
    if agent_name:
        prefix = f"{agent_name.upper()}_"
        for env_key, env_val in os.environ.items():
            if env_key.startswith(prefix):
                # Parse: IT_NEWS_AI_API_KEY -> config["ai"]["api_key"]
                parts = env_key[len(prefix):].lower().split("_", 1)
                if len(parts) == 2:
                    section, key = parts
                    if section not in config:
                        config[section] = {}
                    config[section][key] = _parse_env_value(env_val)
                    logger.debug(f"环境变量覆盖: {env_key} -> config[{section}][{key}]")
                elif len(parts) == 1:
                    # Top-level: AGENT_NAME_MODE = "production"
                    config[parts[0]] = _parse_env_value(env_val)

    return config


def _parse_env_value(value: str) -> Any:
    """Parse environment variable value to appropriate type."""
    # Boolean
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False

    # Number
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    # JSON (for complex values)
    if value.startswith("{") or value.startswith("["):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

    # String
    return value


def save_config(config: Dict[str, Any], path: str) -> bool:
    """Save config to JSON file."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logger.info(f"配置已保存: {path}")
        return True
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return False
