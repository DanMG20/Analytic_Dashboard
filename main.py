import sys
import subprocess
from api.youtube_auth import YoutubeAuth
from api.youtube_data import YouTubeData
from api.youtube_analytics import YouTubeAnalytics
from api.data_builder import DataBuilder
from database.connection import DatabaseManager
from database.repository import YoutubeRepository
from services.updater import Updater
from scheduler.trigger import Scheduler
from utils.logger import get_logger
from utils.paths import data_path
from config import DB_NAME, SCHEDULER_DEFAULT_HOUR, SCHEDULER_DEFAULT_MINUTE
logger = get_logger(__name__)


def launch_dashboard(wait: bool = True) -> None:
    """
    Launches the Streamlit UI as a managed subprocess.
    
    Using a subprocess avoids the 'ValueError: signal only works in main thread'
    which occurs when trying to launch Streamlit from a scheduler thread.
    
    Args:
        wait: If True, blocks execution until the dashboard is closed.
    """
    dashboard_path = "ui/dashboard.py"
    
    # We use sys.executable to ensure we use the same virtual environment
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]
    
    try:
        if wait:
            # Manual mode: Wait for the user to finish
            subprocess.run(cmd, check=True)
        else:
            # Scheduled mode: Fire and forget so the scheduler stays alive
            subprocess.Popen(cmd)
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}")


def build_updater() -> Updater:
    """
    Dependency injection container for the application services.
    
    Returns:
        A fully configured Updater instance.
    """
    db_path = data_path(DB_NAME)
    db_manager = DatabaseManager(db_path)
    repository = YoutubeRepository(db_manager)

    youtube_auth = YoutubeAuth()
    yt_data = YouTubeData(youtube_auth)
    yt_analytics = YouTubeAnalytics(youtube_auth)
    data_builder = DataBuilder(yt_data, yt_analytics)

    return Updater(
        repository=repository,
        data_builder=data_builder,
        yt_data=yt_data
    )


def main() -> None:
    """
    Main orchestration logic. 
    
    Configured to trigger at 11:00 AM. In scheduled mode, it 
    redefines the update task to include the UI launch.
    """
    updater = build_updater()

    if "--scheduled" in sys.argv:
        original_run = updater.run

        def task_with_ui():
            original_run()
            logger.info("Daily update finished. Opening dashboard...")
            launch_dashboard(wait=False)

        updater.run = task_with_ui
        
        scheduler = Scheduler(updater)
        scheduler.start(hour=SCHEDULER_DEFAULT_HOUR, minute=SCHEDULER_DEFAULT_MINUTE)
        return

    updater.run()

    logger.info("Launching dashboard...")
    launch_dashboard(wait=True)


if __name__ == "__main__":
    main()