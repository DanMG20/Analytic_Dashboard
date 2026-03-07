from datetime import date
from typing import Optional, Tuple
from api.data_builder import DataBuilder
from services.data_processor import DataProcessor
from database.repository import YoutubeRepository
from api.youtube_data import YouTubeData
from utils.logger import get_logger

logger = get_logger(__name__)


class Updater:
    """
    Orchestrates the main ETL flow for YouTube statistics.

    This class handles the decision-making process regarding when and 
    what data should be updated based on the current database state.
    """

    def __init__(
        self,
        repository: YoutubeRepository,
        data_builder: DataBuilder,
        yt_data: YouTubeData
    ):
        """
        Initializes the updater with required data and persistence services.

        Args:
            repository: Service handling database operations.
            data_builder: Service handling multi-API data extraction.
            yt_data: Client for YouTube Data API basic requests.
        """
        self.repository = repository
        self.data_builder = data_builder
        self.yt_data = yt_data

    def run(self) -> None:
        """
        Executes the end-to-end synchronization process.

        It checks the last update, calculates the missing date range,
        extracts raw data, transforms it, and persists the results.
        """
        logger.info("Starting update cycle...")

        last_updated = self.repository.get_last_updated_date()
        channel_info = self.yt_data.get_channel_data()

        if not channel_info:
            logger.error("Channel info retrieval failed. Aborting.")
            return

        creation_date = DataProcessor.parse_iso_date(
            channel_info.creation_date
        )

        start_date, end_date = self.get_range_date(
            last_updated,
            creation_date
        )

        if start_date is None:
            logger.info("System is already up to date.")
            return

        try:
            logger.info(f"Syncing from {start_date} to {end_date}")
            raw_data = self.data_builder.build(start_date, end_date)

            processor = DataProcessor(raw_data)
            ch_stats, daily_m, video_m = processor.process_all()

            self.repository.save_all(ch_stats, daily_m, video_m)
            logger.info("Update completed successfully.")

        except Exception as e:
            logger.error(f"Critical error during ETL flow: {e}")

    def get_range_date(
        self,
        last_update: Optional[date],
        channel_creation: date
    ) -> Tuple[Optional[date], Optional[date]]:
        """
        Calculates the sync window based on previous records.

        Args:
            last_update: The latest date found in the database.
            channel_creation: The date the channel was first published.

        Returns:
            A tuple of (start_date, end_date) or (None, None) if up to date.
        """
        start_date = self._verify_last_update(last_update, channel_creation)

        if start_date is None:
            return None, None

        return start_date, date.today()

    def _verify_last_update(
        self,
        last_update: Optional[date],
        channel_creation: date
    ) -> Optional[date]:
        """
        Validates the starting point for the update process.

        Args:
            last_update: Timestamp of the last successful synchronization.
            channel_creation: Fallback date if no database records exist.

        Returns:
            The validated start date or None if no update is required.
        """
        if last_update is None:
            return channel_creation

        if last_update >= date.today():
            return None

        return last_update