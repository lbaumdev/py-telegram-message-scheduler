from telegram import Update

from database import get_database


async def list_all(update: Update) -> None:
    if update.effective_chat.type != "private":
        return

    database = get_database()
    cur_str = 'Current jobs:'

    for job in database['jobs']:
        cur_str += '\n\n'
        cur_str += f"\t\tName: {job['name']}\n"
        cur_str += f"\t\tChatID: {job['chat_id']}\n"
        cur_str += f"\t\tSchedule: {job['schedule']}\n"
        cur_str += f"\t\tMessage: {job['message']}\n"
    else:
        cur_str = 'No jobs registered\n'

    await update.message.reply_text(cur_str)

