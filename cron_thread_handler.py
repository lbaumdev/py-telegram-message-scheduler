import logging
import time

import pycron
import telegram

from config import get_env_var, EnvVars
from database import get_all_jobs

logger = logging.getLogger(__name__)

SYNC_INTERVAL_MINUTES = get_env_var(EnvVars.SYNC_INTERVAL_MINUTES, 10)


def minute_passed(old_epoch: int, minutes: int) -> bool:
    return time.time() - old_epoch >= (60 * minutes)


async def cron_thread_func():
    logger.info("Cron thread started!")
    bot = telegram.Bot(get_env_var(EnvVars.TELEGRAM_BOT_TOKEN))

    jobs = get_all_jobs()

    last_sync = time.time()
    while True:
        job_triggered = False
        for job in jobs:
            if pycron.is_now(job["schedule"]):
                logger.info(f"Sending message to {job['target_chat_id']} for job {job['name']}")

                await bot.sendMessage(job["target_chat_id"], job["message"])
                job_triggered = True
            else:
                job_triggered = False

        if job_triggered:
            time.sleep(60)
        else:
            time.sleep(30)

        if minute_passed(last_sync, SYNC_INTERVAL_MINUTES):
            jobs = get_all_jobs()
            last_sync = time.time()
            logger.info("Synced jobs within cron thread.")
