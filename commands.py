import logging

from cron_descriptor import ExpressionDescriptor, CasingTypeEnum
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from database import get_my_jobs, get_my_chats, delete_chat, delete_job
from telegram.ext import ContextTypes, CallbackContext

from lang import translate

logger = logging.getLogger(__name__)

COMMANDS = {
    "create": translate("command.create"),
    "list": translate("command.list"),
    "help": translate("command.help"),
}


def available_commands():
    message = [translate("available-commands")]
    for command, description in COMMANDS.items():
        message.append(f"\t\t\t/{command}: {description}")

    return '\n'.join(message)


async def start(update: Update, context: CallbackContext):
    message = [
        translate("start-greeting-bot") + "\n",
        available_commands()
    ]

    await update.message.reply_text('\n'.join(message))


async def help_command(update: Update, context: CallbackContext):
    # allows use of this command only in private chats
    if update.effective_chat.type != "private":
        return

    await update.message.reply_text(available_commands())


async def list_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # allows use of this command only in private chats
    if update.effective_chat.type != "private":
        return

    my_jobs = get_my_jobs(update.effective_user.id)
    cur_str = translate("registered-jobs")

    if len(my_jobs) > 0:
        for job in my_jobs:
            descriptor = ExpressionDescriptor(
                expression=job['schedule'],
                casing_type=CasingTypeEnum.Sentence,
                use_24hour_time_format=True
            )

            cur_str += '\n\n'
            cur_str += f"{translate("job.name")}: {job['name']}\n"
            cur_str += f"{translate("job.chat_id")}: {job['target_chat_id']}\n"
            cur_str += f"{translate("job.schedule")}: {descriptor.get_description()}\n"
            cur_str += f"{translate("job.message")}:\n{job['message']}"
    else:
        cur_str = f'{translate("no-jobs-registered")}\n'

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

        await update.message.reply_text(translate("choose-job-for-deletion"),
                                        reply_markup=reply_markup)
    else:
        await update.message.reply_text(translate("no-jobs-registered"))


async def delete_job_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    job_id = query.data

    delete_job(job_id, update.effective_user.id)

    await query.edit_message_text(translate("job-deleted-successfully"))
