from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import get_env_var, EnvVars


async def inform_devs(context: ContextTypes.DEFAULT_TYPE, message: str):
    developer_chat_id = get_env_var(EnvVars.DEVELOPER_CHAT_ID)
    if developer_chat_id:
        devs = developer_chat_id.split(",")
        for dev in devs:
            await context.bot.send_message(
                chat_id=dev.strip(), text=message, parse_mode=ParseMode.HTML
            )