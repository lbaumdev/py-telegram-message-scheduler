import datetime
import logging
import sqlite3
from contextlib import closing

logger = logging.getLogger(__name__)

DB_FILENAME = "data/database.db"


def insert_chat(title, telegram_chat_id, adder_id):
    with sqlite3.connect(DB_FILENAME) as connection:
        with closing(connection.cursor()) as cursor:
            created_at = datetime.datetime.now()

            cursor.execute(
                "INSERT INTO chats (title, telegram_chat_id, adder_id, created_at) VALUES (?, ?, ?, ?)",
                (title, telegram_chat_id, adder_id, created_at)
            )
            connection.commit()

            logger.debug(f"Inserted chat ({cursor.lastrowid}) into database")

            return cursor.lastrowid


def delete_chat(telegram_chat_id: str, adder_id: str) -> int:
    with sqlite3.connect(DB_FILENAME) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                "DELETE FROM chats WHERE telegram_chat_id = ? AND adder_id = ?",
                (telegram_chat_id, adder_id)
            )

            connection.commit()

            logger.debug(
                f"Deleted chat (rowCount: {cursor.rowcount}) with telegram_chat_id {telegram_chat_id} and adder_id {adder_id}  from database")

            return cursor.rowcount


def delete_chat_by_telegram_id(chat_id: str, adder_id: str) -> int:
    with sqlite3.connect(DB_FILENAME) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                "DELETE FROM chats WHERE id = ? AND adder_id = ?",
                (chat_id, adder_id)
            )
            connection.commit()

            logger.debug(
                f"Deleted chat (rowCount: {cursor.rowcount}) with id {chat_id} and adder_id {adder_id} from database")

            return cursor.rowcount


def get_my_jobs(user_id: str, include_chat_metadata: bool = False):
    logger.info(f"Getting my jobs for user {user_id}")
    with sqlite3.connect(DB_FILENAME) as connection:
        connection.row_factory = sqlite3.Row

        with closing(connection.cursor()) as cursor:
            query = "SELECT * FROM jobs WHERE owner_id = ?"

            if include_chat_metadata:
                query = "SELECT * FROM jobs INNER JOIN chats WHERE owner_id = ?"

            cursor.execute(
                query,
                (user_id,)
            )
            jobs = cursor.fetchall()
            return jobs


def insert_job(name: str, message: str, schedule: str, owner_id: str, target_chat_id: str):
    with sqlite3.connect(DB_FILENAME) as connection:
        with closing(connection.cursor()) as cursor:
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()

            cursor.execute(
                "INSERT INTO jobs (name, message, schedule, owner_id, created_at, updated_at, target_chat_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, message, schedule, owner_id, created_at, updated_at, target_chat_id)
            )
            connection.commit()

            logger.debug(f"Inserted job {cursor.lastrowid} (rowCount: {cursor.rowcount}) into database")

            return cursor.lastrowid


def get_all_jobs():
    with sqlite3.connect(DB_FILENAME) as connection:
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                "SELECT name, message, schedule, owner_id, target_chat_id FROM jobs "
            )
            jobs = cursor.fetchall()
            return jobs


def get_my_chats(user_id: str):
    with sqlite3.connect(DB_FILENAME) as connection:
        connection.row_factory = sqlite3.Row

        with closing(connection.cursor()) as cursor:
            cursor.execute(
                "SELECT title, telegram_chat_id, adder_id FROM chats WHERE adder_id = ?",
                (user_id,)
            )
            chats = cursor.fetchall()
            return chats
