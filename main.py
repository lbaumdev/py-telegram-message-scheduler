#!/usr/bin/env python
import asyncio
import json
import logging
import os
import threading
import re

from telegram import Update, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler, \
    ConversationHandler, MessageHandler, filters, CallbackQueryHandler

import error_handler
from lang import translate
from chat import track_chats
from commands import list_all, delete, start, help_command, delete_job_button
from config import get_env_var, load_env, EnvVars
from cron_thread_handler import cron_thread_func
from database import get_my_chats, insert_job, migrate_database

log_name = "./logs/telegram.log"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_name),
        logging.StreamHandler()
    ]
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

MESSAGE_CONTENT, TARGET_CHAT, SCHEDULE, JOB_NAME, FINAL = range(5)
job_map = {}


def is_owner(user_id: str):
    logger.warning(f"is_owner: {user_id}")
    bot_owners = os.getenv("TELEGRAM_BOT_OWNER_ID")
    if bot_owners:
        found = False
        for bot_owner in bot_owners.split(","):
            if str(user_id) == str(bot_owner):
                found = True
                break

        return found
    else:
        return False


async def start_creation_of_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        logger.info(f"User with id: {update.effective_user.id} is not owner!")
        return ConversationHandler.END

    await update.message.reply_text(
        translate("greeting") + translate("questions") + translate("question-1")
    )

    return JOB_NAME


async def job_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job_map[f"{update.effective_user.id}-{update.effective_chat.id}"] = {
        "name": update.message.text
    }

    chats = get_my_chats(update.effective_user.id)

    if len(chats) == 0:
        # Enter custom chat id
        await update.message.reply_text(
            translate("no-chats-found")
        )
        return ConversationHandler.END

    keyboard = []

    for chat in chats:
        keyboard_button = InlineKeyboardButton(f"{chat['title']} ({chat['telegram_chat_id']})")
        keyboard.append(keyboard_button)

    reply_markup = ReplyKeyboardMarkup([keyboard])

    await update.message.reply_text(translate("question-2"),
                                    reply_markup=reply_markup)

    return TARGET_CHAT


async def target_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    regex = r'\((.*?)\)'
    job_map[f"{update.effective_user.id}-{update.effective_chat.id}"]["chat_id"] = \
        re.findall(regex, update.message.text)[0]

    await update.message.reply_text(
        translate("question-3"),
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text=translate("open-scheduler-web-app"),
                web_app=WebAppInfo(
                    url=get_env_var(
                        EnvVars.TELEGRAM_SCHEDULER_WEB_APP_URL,
                        "https://lbaumdev.github.io"
                    )
                ),
            )
        ),
    )

    return SCHEDULE


# Handle incoming WebAppData for schedule
async def web_app_schedule_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print the received data and remove the button."""

    data = json.loads(update.effective_message.web_app_data.data)
    logger.info(f"Data from Webapp: {data['expression']}")

    job_map[f"{update.effective_user.id}-{update.effective_chat.id}"]["schedule"] = data['expression']

    await update.message.reply_html(
        text=translate("question-4"),
        reply_markup=ReplyKeyboardRemove()
    )
    return MESSAGE_CONTENT


async def message_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    job_map[f"{update.effective_user.id}-{update.effective_chat.id}"]["message"] = update.message.text

    await update.message.reply_text(
        translate("job-created")
    )

    current_job = job_map[f"{update.effective_user.id}-{update.effective_chat.id}"]
    logger.debug(current_job)

    insert_job(
        current_job["name"],
        current_job["message"],
        current_job["schedule"],
        update.effective_user.id,
        current_job["chat_id"],
        update.effective_chat.id,
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.first_name} canceled the conversation.")
    await update.message.reply_text(
        translate("conversation-canceled-by-user"), reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


if __name__ == '__main__':
    load_env()

    logger.info("Starting migration...")
    migrate_database()
    logger.info("Migration complete.")

    logger.info("Starting Telegram Scheduled Messenger Bot...")

    cron_thread = threading.Thread(target=asyncio.run, args=(cron_thread_func(),))
    cron_thread.start()

    app = ApplicationBuilder().token(get_env_var(EnvVars.TELEGRAM_BOT_TOKEN)).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_all))
    app.add_handler(CommandHandler("delete", delete))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", start_creation_of_job)],
        states={
            MESSAGE_CONTENT: [MessageHandler(filters.TEXT, message_content)],
            TARGET_CHAT: [MessageHandler(filters.TEXT, target_chat)],
            SCHEDULE: [MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_schedule_data)],
            JOB_NAME: [MessageHandler(filters.TEXT, job_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    app.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_schedule_data))
    app.add_handler(CallbackQueryHandler(delete_job_button))

    app.add_error_handler(error_handler)

    app.run_polling()
