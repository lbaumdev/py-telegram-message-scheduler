import asyncio
import logging
import os
import sys
import threading
import time
import re

import pycron
import telegram

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler, CallbackQueryHandler, \
    ConversationHandler, MessageHandler, filters

from chat_helpers import track_chats
from commands import list_all
from config_helpers import get_bot_token, load_env
from database import save_to_database, get_database, create_db_if_not_exists

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

data = None
MESSAGE_CONTENT, TARGET_CHAT, SCHEDULE, JOB_NAME, FINAL = range(5)
current_job = {
    "name": None,
    "chat_id": None,
    "schedule": None,
    "message": None,
}


async def sync_jobs_to_database() -> None:
    save_to_database(data)


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

def between_callback():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(cron_thread_func())
    loop.close()


async def cron_thread_func():
    logger.info("Cron thread started!")
    bot = telegram.Bot(get_bot_token())
    logger.info(get_database())
    jobs = get_database()['jobs']

    cron_thread_running = True
    while cron_thread_running:
        job_triggered = False
        for job in jobs:
            if pycron.is_now(job["schedule"]):
                logger.info(f"Sending message to {job['chat_id']} for job {job['name']}")

                await bot.sendMessage(job["chat_id"], job["message"])
                job_triggered = True
            else:
                job_triggered = False

        if job_triggered:
            time.sleep(60)
        else:
            time.sleep(30)


async def start_creation_of_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        logger.info(f"User with id: {update.effective_user.id} is not owner!")
        return ConversationHandler.END

    await update.message.reply_text(
        "Hi! My name is Py Ad Manager Bot. I will ask you some questions.\n"
        "1. Message Content\n"
        "2. Target Chat\n"
        "3. Schedule (time the message will be sent)\n"
        "4. Custom name of the job\n"
        "Send /cancel to stop talking to me.\n\n"
        "Whats your message to send?"
    )

    return MESSAGE_CONTENT


async def message_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_job["message"] = update.message.text

    database = get_database()

    keyboard = []

    for chat_id, values in database['chats'].items():
        keyboard_button = InlineKeyboardButton(f"{values['title']} ({values['id']})")
        keyboard.append(keyboard_button)

    reply_markup = ReplyKeyboardMarkup([keyboard])

    await update.message.reply_text("Please choose a chat to send the message to (bot must be member):",
                                    reply_markup=reply_markup)

    return TARGET_CHAT


async def target_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    regex = r'\((.*?)\)'
    current_job["chat_id"] = re.findall(regex, update.message.text)[0]

    await update.message.reply_text(
        "When should your message be sent? (Schedule)\n"
        "Format: '*/1 * * * *' (means every minute)"
        "Use https://crontab.guru/ for help",
        reply_markup=ReplyKeyboardRemove(),
    )

    return SCHEDULE


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_job["schedule"] = update.message.text

    await update.message.reply_text("Enter a custom name for this job (e.g. newsletter reminder)")

    return JOB_NAME


async def job_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_job["name"] = update.message.text
    await update.message.reply_text(
        "Awesome. The job is now registered and ready. The conversation is over."
    )

    logger.info(current_job)
    database = get_database()
    payload = {
        "name": current_job["name"],
        "chat_id": current_job["chat_id"],
        "message": current_job["message"],
        "schedule": current_job["schedule"]
    }
    database["jobs"].append(payload)
    save_to_database(database)
    cron_thread.join()
    cron_thread.start()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.first_name} canceled the conversation.")
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


if __name__ == '__main__':
    cron_thread = threading.Thread(target=between_callback)

    try:
        logger.info("Starting Telegram Scheduled Messenger Bot...")

        load_env()

        create_db_if_not_exists()

        cron_thread.start()

        app = ApplicationBuilder().token(get_bot_token()).build()

        app.add_handler(CommandHandler("list", list_all))

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("create", start_creation_of_job)],
            states={
                MESSAGE_CONTENT: [MessageHandler(filters.TEXT, message_content)],
                TARGET_CHAT: [MessageHandler(filters.TEXT, target_chat)],
                SCHEDULE: [MessageHandler(filters.TEXT, schedule)],
                JOB_NAME: [MessageHandler(filters.TEXT, job_name)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )

        app.add_handler(conv_handler)

        app.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))

        app.run_polling()

    except (KeyboardInterrupt, SystemExit):
        cron_thread.join()
        sys.exit()
