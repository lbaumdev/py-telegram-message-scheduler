import logging
from typing import Optional

from telegram import ChatMember, Update, Chat, ChatMemberUpdated
from telegram.ext import ContextTypes

from database import insert_chat, delete_chat

logger = logging.getLogger(__name__)


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member",
        (None, None)
    )

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


# NOTE: this function must be async
async def track_chats(update: Update,
                context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return

    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name, cause_id = update.effective_user.full_name, update.effective_user.id

    # Handle chat types differently:
    chat = update.effective_chat
    user = update.effective_user
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info(
                f"{cause_name} ({cause_id}) added the bot to the group {chat.title}")
            insert_chat(chat.title, chat.id, user.id)
        elif was_member and not is_member:
            logger.info(
                f"{cause_name} ({cause_id}) removed the bot from the group {chat.title}")
            delete_chat(chat.id, user.id)
    elif not was_member and is_member:
        logger.info(f"{cause_name} ({cause_id}) added the bot to the channel {chat.title}")
        insert_chat(chat.title, chat.id, user.id)
    elif was_member and not is_member:
        logger.info(
            f"{cause_name} ({cause_id}) removed the bot from the channel {chat.title}")
        delete_chat(chat.id, user.id)
