"""
Logger setup - loguru configuration for all agents.
"""
import sys
import os
from pathlib import Path
from loguru import logger


def setup_logger(
    name: str = "agent",
    level: str = "INFO",
    log_dir: str = None,
    rotation: str = "20 MB",
    retention: str = "7 days",
) -> None:
    """
    Configure loguru for the agent.

    Args:
        name: Logger name (used as filename prefix)
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files (default: {agent_dir}/logs)
        rotation: When to rotate log files
        retention: How long to keep old logs
    """
    # Remove default handler
    logger.remove()

    # Console output (always)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )

    # File output (if log_dir specified)
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Main log file
        logger.add(
            log_path / f"{name}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {function}:{line} | {message}",
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            encoding="utf-8",
        )

        # Error log file
        logger.add(
            log_path / f"{name}_error.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {function}:{line} | {message}",
            level="ERROR",
            rotation=rotation,
            retention=retention,
            compression="zip",
            encoding="utf-8",
        )
