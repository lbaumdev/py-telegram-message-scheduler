import logging

from cron_descriptor import ExpressionDescriptor, CasingTypeEnum
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from config import get_env_var, EnvVars
from database import get_my_jobs, get_my_chats, delete_chat
from telegram.ext import ContextTypes, CallbackContext

logger = logging.getLogger(__name__)

COMMANDS = {
    "create": "Creates a scheduled job to send a custom message",
    "help": "Get description of available commands"
}


async def start(update: Update, context: CallbackContext):
    message = [
        f"Hello, I can create jobs for sending scheduled messages. Use one of the listed commands.",
        "\nAvailable commands:"]
    for command, description in COMMANDS.items():
        message.append(f"\t\t\t/{command}: {description}")

    await update.message.reply_text('\n'.join(message))


async def help_command(update: Update, context: CallbackContext):
    # allows use of this command only in private chats
    if update.effective_chat.type != "private":
        return

    message = ["Available commands:"]
    for command, description in COMMANDS.items():
        message.append(f"\t\t\t/{command}: {description}")

    await update.message.reply_text('\n'.join(message))


async def list_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # allows use of this command only in private chats
    if update.effective_chat.type != "private":
        return

    my_jobs = get_my_jobs(update.effective_user.id)
    cur_str = "Registered jobs: "

    if len(my_jobs) > 0:
        for job in my_jobs:
            descriptor = ExpressionDescriptor(
                expression=job['schedule'],
                casing_type=CasingTypeEnum.Sentence,
                use_24hour_time_format=True
            )

            cur_str += '\n\n'
            cur_str += f"\t\tName: {job['name']}\n"
            cur_str += f"\t\tChatID: {job['target_chat_id']}\n"
            cur_str += f"\t\tSchedule: {descriptor.get_description()}\n"
            cur_str += f"\t\tMessage:\n\n {job['message']}\n"
    else:
        cur_str = 'No jobs registered\n'

    await update.message.reply_text(cur_str)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # allows use of this command only in private chats
    if update.effective_chat.type != "private":
        return

    keyboard = []

    my_jobs = get_my_jobs(update.effective_user.id, True)

    if len(my_jobs):
        for job in my_jobs:
            print(dict(job))
            keyboard_button = InlineKeyboardButton(
                f"{job['title']} ({job['target_chat_id']})", callback_data=job["id"])
            keyboard.append(keyboard_button)

        reply_markup = InlineKeyboardMarkup([keyboard])

        await update.message.reply_text("Please choose a chat to delete:",
                                        reply_markup=reply_markup)
    else:
        await update.message.reply_text("No jobs registered")

async def delete_job_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    chat_id = query.data

    delete_chat(chat_id, update.effective_user.id)

    await query.edit_message_text(f"Job deleted successfully!")
