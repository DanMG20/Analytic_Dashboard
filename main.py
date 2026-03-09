import multiprocessing
import os
import subprocess
import sys

from api.data_builder import DataBuilder
from api.youtube_analytics import YouTubeAnalytics
from api.youtube_auth import YoutubeAuth
from api.youtube_data import YouTubeData
from config import DB_NAME, SCHEDULER_DEFAULT_HOUR, SCHEDULER_DEFAULT_MINUTE
from database.connection import DatabaseManager
from database.repository import YoutubeRepository
from scheduler.trigger import Scheduler
from services.updater import Updater
from utils.logger import get_logger
from utils.paths import data_path, get_base_dir

logger = get_logger(__name__)


def build_updater() -> Updater:
    """Dependency injection container for the application services."""
    db_path = str(data_path(DB_NAME))
    db_manager = DatabaseManager(db_path)
    repository = YoutubeRepository(db_manager)

    youtube_auth = YoutubeAuth()
    yt_data = YouTubeData(youtube_auth)
    yt_analytics = YouTubeAnalytics(youtube_auth)
    data_builder = DataBuilder(yt_data, yt_analytics)

    return Updater(repository=repository, data_builder=data_builder, yt_data=yt_data)


def launch_dashboard(wait: bool = True) -> None:
    """Launches the Streamlit UI safely, injecting environment variables for sub-processes."""
    dashboard_path = str(get_base_dir() / "ui" / "dashboard.py")

    # EL TRUCO: Creamos una variable de entorno para heredar a los procesos hijos de Streamlit
    env = os.environ.copy()
    env["IS_STREAMLIT_PROCESS"] = "1"

    if getattr(sys, "frozen", False):
        cmd = [sys.executable, "run_ui", dashboard_path]
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]

    try:
        if wait:
            subprocess.run(cmd, env=env, check=True)
        else:
            subprocess.Popen(cmd, env=env)
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}")


def main() -> None:
    """Main orchestration logic with Streamlit interceptor for compiled apps."""

    if os.environ.get("IS_STREAMLIT_PROCESS") == "1":
        import streamlit.web.cli as stcli

        if len(sys.argv) > 1 and sys.argv[1] == "run_ui":
            sys.argv = [
                "streamlit",
                "run",
                sys.argv[2],
                "--global.developmentMode=false",
            ]

        elif len(sys.argv) > 2 and sys.argv[1] == "-m" and sys.argv[2] == "streamlit":
            sys.argv = ["streamlit"] + sys.argv[3:]

        sys.exit(stcli.main())

    updater = build_updater()

    if "--scheduled" in sys.argv:
        original_run = updater.run

        def task_with_ui() -> None:
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
    multiprocessing.freeze_support()
    main()
