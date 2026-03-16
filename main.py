import sys
import webbrowser

from api.data_builder import DataBuilder
from api.youtube_analytics import YouTubeAnalytics
from api.youtube_auth import YoutubeAuth
from api.youtube_data import YouTubeData
from config import (DB_NAME, POWER_BI_REPORT_URL, SCHEDULER_DEFAULT_HOUR,
                    SCHEDULER_DEFAULT_MINUTE)
from database.connection import DatabaseManager
from database.repository import YoutubeRepository
from scheduler.trigger import Scheduler
from services.updater import Updater
from utils.logger import get_logger
from utils.paths import data_path

logger = get_logger(__name__)


def build_updater() -> Updater:
    """
    Dependency injection container for the application services.

    Returns:
        Updater: A fully configured instance of the Updater service.
    """
    db_path = str(data_path(DB_NAME))
    db_manager = DatabaseManager(db_path)
    repository = YoutubeRepository(db_manager)

    youtube_auth = YoutubeAuth()
    yt_data = YouTubeData(youtube_auth)
    yt_analytics = YouTubeAnalytics(youtube_auth)
    data_builder = DataBuilder(yt_data, yt_analytics)

    return Updater(repository=repository, data_builder=data_builder, yt_data=yt_data)


def launch_power_bi_dashboard(url: str) -> None:
    """
    Opens the specified Power BI dashboard URL in the system's default web browser.

    Args:
        url: The web link targeting the Power BI report.
    """
    logger.info(f"Attempting to open Power BI dashboard at: {url}")
    try:
        # webbrowser.open returns a boolean indicating success
        is_opened = webbrowser.open(url)
        if not is_opened:
            logger.warning("Could not open the default web browser automatically.")
    except webbrowser.Error as browser_error:
        logger.error(
            f"Failed to launch web browser due to an internal error: {browser_error}"
        )


def main() -> None:
    """
    Main orchestration logic.
    Executes the ETL process and manages the browser invocation.
    """
    updater = build_updater()

    # Scheduled Daemon Mode
    if "--scheduled" in sys.argv:
        original_run = updater.run

        def task_with_ui() -> None:
            """
            Wraps the core run execution to automatically open the UI upon completion.
            """
            original_run()
            logger.info("Daily update finished successfully.")
            launch_power_bi_dashboard(POWER_BI_REPORT_URL)

        updater.run = task_with_ui
        scheduler = Scheduler(updater)
        scheduler.start(hour=SCHEDULER_DEFAULT_HOUR, minute=SCHEDULER_DEFAULT_MINUTE)
        return

    # Immediate Execution Mode
    updater.run()
    logger.info("Initial synchronization complete.")
    launch_power_bi_dashboard(POWER_BI_REPORT_URL)


if __name__ == "__main__":
    main()
