import logging
from typing import Optional

from telegram import ChatMember, Update, Chat, ChatMemberUpdated
from telegram.ext import ContextTypes

from database import get_database, save_to_database

logger = logging.getLogger(__name__)


def extract_status_change(
        chat_member_update: ChatMemberUpdated) -> Optional[tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update,
                      context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name = update.effective_user.full_name

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info(
                f"{cause_name} added the bot to the group {chat.title}")
            add_chat(chat.id, chat.title)
        elif was_member and not is_member:
            logger.info(
                f"{cause_name} removed the bot from the group {chat.title}")
            remove_chat(chat.id)
    elif not was_member and is_member:
        logger.info(f"{cause_name} added the bot to the channel {chat.title}")
        add_chat(chat.id, chat.title)
    elif was_member and not is_member:
        logger.info(
            f"{cause_name} removed the bot from the channel {chat.title}")
        remove_chat(chat.id)


def add_chat(chat_id: str, chat_title: str) -> None:
    logger.info("Add chat to database: {chat_title}")
    database = get_database()
    database["chats"][chat_id] = {
        "id": chat_id,
        "title": chat_title,
    }
    save_to_database(database)


def remove_chat(chat_id: str) -> None:
    logger.info(f"Remove chat from database: {chat_id}")
    database = get_database()
    if chat_id in database["chats"]:
        del database["chats"][chat_id]
        save_to_database(database)
    else:
        logger.info(f"{chat_id} not in database")
