import sys
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

logger = get_logger(__name__)


def main():
    """
    Bootstraps the infrastructure and selects the execution mode.
    """
    db_path = data_path("youtube_stats.db")
    db_manager = DatabaseManager(db_path)
    repository = YoutubeRepository(db_manager)

    youtube_auth = YoutubeAuth()
    yt_data = YouTubeData(youtube_auth)
    yt_analytics = YouTubeAnalytics(youtube_auth)
    data_builder = DataBuilder(yt_data, yt_analytics)

    updater = Updater(
        repository=repository,
        data_builder=data_builder,
        yt_data=yt_data
    )

    if "--scheduled" in sys.argv:
        scheduler = Scheduler(updater)
        scheduler.start(hour=3, minute=0)
    else:
        updater.run()


if __name__ == "__main__":
    main()