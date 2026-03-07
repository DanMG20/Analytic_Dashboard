from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from services.updater import Updater
from utils.logger import get_logger

logger = get_logger(__name__)


class Scheduler:
    """
    Handles the automated execution of the YouTube ETL process.

    This class wraps the APScheduler to trigger the Updater based on
    predefined cron expressions.
    """

    def __init__(self, updater: Updater):
        """
        Initializes the scheduler with the required orchestrator.

        Args:
            updater: The service responsible for the ETL execution.
        """
        self.updater = updater
        self.scheduler = BlockingScheduler()

    def start(self, hour: int = 3, minute: int = 0) -> None:
        """
        Configures and starts the cron job.

        Args:
            hour: Hour of the day to trigger (0-23).
            minute: Minute of the hour to trigger (0-59).
        """
        trigger = CronTrigger(hour=hour, minute=minute)

        self.scheduler.add_job(
            func=self.updater.run,
            trigger=trigger,
            id="youtube_etl_sync",
            name="Daily YouTube Sync",
            replace_existing=True
        )

        logger.info(f"Scheduler started. Job scheduled daily at {hour:02d}:{minute:02d}")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped manually.")