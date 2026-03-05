from api.youtube_auth import YoutubeAuth
from models.daily_stats import DailyStats
from typing import Any ,Optional
from datetime import date
from utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeAnalytics:
    """
    Gateway to interact with Youtube Analytics API v2. 
    """


    def __init__(self, outh_client: YoutubeAuth):
        """
        Initializes the service using an authenticated client.
        """
        self.service = outh_client.get_service("youtubeAnalytics","v2")

    def get_daily_stats(self,start_date,end_date) -> Optional[DailyStats]:
        """
        Fetches historical data sorted by date. 

        Returns:
            Optional[HistoricalDataPerDay]: The validated data or None if not found. 
        """
        response = self._request_historical_data_per_date(
            start_date=start_date,
            end_date= end_date)

        rows = response.get('rows',[])

        if not rows: 
            logger.warning("Data not found for the autenticated user")
            return None 
        logger.info("Historical data per day obtained")

        return self._build_data(rows=rows)

    def _request_historical_data_per_date(
            self, 
            start_date: date, 
            end_date : date, 
        ) -> dict[str, Any]:
        """
        Retrieves historical metrics per day in a specific date range.

        """
        return self.service.reports().query(
            ids= "channel==MINE", 
            startDate = start_date.isoformat(),
            endDate = end_date.isoformat(),
            metrics = "views,subscribersGained,averageViewDuration",
            dimensions = "day",
            sort ="day"
        ).execute()

    def _map_daily_stats(
            self,
            row:list[str]) -> DailyStats:
        """
        Maps the raw API JSON data to a DailyStats.
        """
        return DailyStats(
            date = row[0],
            views = int(row[1]),
            subs_gained = int(row[2]),
            avg__view_duration= int(row[3])

        )
    
    def _build_data(self, rows)-> list[str,int,int,int]:
        """
        Builds the list of metrics.
        Returns:
            list[str,int,int,int]: range for daily metrics
        """
        data = []
        for row in rows:
            day_stats = self._map_daily_stats(row)
            data.append(day_stats)
        return data 



