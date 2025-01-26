import logging
import time

import pycron
import telegram

from config import get_env_var, EnvVars
from database import get_all_jobs, delete_job
from lang import translate

logger = logging.getLogger(__name__)


def minute_passed(old_epoch: int, minutes: int) -> bool:
    now = time.time()
    return now - old_epoch >= (60 * minutes)


async def cron_thread_func():
    SYNC_INTERVAL_MINUTES = int(get_env_var(EnvVars.SYNC_INTERVAL_IN_MINUTES, "10"))

    logger.info("Cron thread started!")
    bot = telegram.Bot(get_env_var(EnvVars.TELEGRAM_BOT_TOKEN))

    jobs = get_all_jobs()

    last_sync = time.time()
    while True:
        job_triggered = False
        for job in jobs:
            if pycron.is_now(job["schedule"]):
                logger.info(f"Sending message to {job['target_chat_id']} for job {job['name']}")

                try:
                    await bot.sendMessage(job["target_chat_id"], job["message"])
                except telegram.error.Forbidden:
                    if job["owner_chat_id"] is not None:
                        await bot.sendMessage(
                            job["owner_chat_id"],
                            translate("error-no-permissions-to-send").replace("{{x}}", job["name"])
                        )
                        delete_job(job_id=job["id"], owner_id=job["owner_id"])
                except Exception as e:
                    logger.error(f"Failed to send message to {job['target_chat_id']} for job {job['name']}")
                    logging.exception(e)

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
