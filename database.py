import json
import logging
import os

logger = logging.getLogger(__name__)

DB_FILENAME = "database.json"


def save_to_database(payload):
    with open(DB_FILENAME, 'w+', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)


def get_database():
    with open(DB_FILENAME, encoding='utf-8') as f:
        return json.load(f)


def create_db_if_not_exists():
    if os.path.isfile(DB_FILENAME):
        logger.info("Database already exists!")
    else:
        logger.info("Creating empty database...")
        save_to_database({
            "jobs": [],
            "chats": {}
        })
        logger.info("Empty database created!")
