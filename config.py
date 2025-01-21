import logging
import os
import sys
from enum import StrEnum

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class EnvVars(StrEnum):
    TELEGRAM_BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'
    SYNC_INTERVAL_IN_MINUTES = 'SYNC_INTERVAL_IN_MINUTES'


def load_env():
    logger.info("Loading environment variables...")
    load_dotenv()

    # checking for required env vars
    if os.getenv("TELEGRAM_BOT_TOKEN") is not None:
        logger.info("Environment variables loaded successfully.")
    else:
        logger.warning("Some environment variables are missing. Errors may occur.")
        sys.exit(1)


def get_env_var(env_var: EnvVars, default=None):
    env_var_value = os.getenv(env_var)
    print(env_var, env_var_value)
    if env_var_value is None:
        env_var_value = default

    return env_var_value
