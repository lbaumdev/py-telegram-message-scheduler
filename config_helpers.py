import logging
import os
import sys

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_env():
    logger.info("Loading dotenv...")
    load_dotenv()
    logger.info("Dotenv loaded.")


def get_bot_token():
    bot_token = os.getenv('BOT_TOKEN')
    if bot_token is None:
        logger.info('Bot token not set. Aborting...')
        sys.exit(0)
    return bot_token