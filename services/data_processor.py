from typing import List, Tuple
from datetime import datetime,date
from models.raw_data import RawData
from database.models import ChannelStats, DailyMetrics, VideoMetrics
from utils.logger import get_logger

logger = get_logger(__name__)

class DataProcessor:
    """Process the raw data obtained from youtube API's."""

    def __init__(self,raw_data: RawData):
        self.raw_data = raw_data

    @staticmethod
    def parse_iso_date(date_str: str) -> date:
        """
        Utility to convert YouTube ISO 8601 strings to Python date objects.
        Handles the 'Z' suffix by replacing it with UTC offset.
        """
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()

    def process_all(self) -> Tuple[ChannelStats, List[DailyMetrics], List[VideoMetrics]]:
        """ 
        Orchestrates the transformation of all raw data into DB entities. 
        """
        logger.info("Starting data transformation of all raw data into DB entities")

        channel_stats = self._transform_channel_stats()
        daily_metrics = self._transform_daily_metrics()
        video_metrics = self._transform_video_metrics()

        return channel_stats, daily_metrics , video_metrics

    def _transform_channel_stats(self) -> ChannelStats:
        api_channel = self.raw_data.channel_data
        
        creation_date =self.parse_iso_date(api_channel.creation_date)

        return ChannelStats(
            name=api_channel.name,
            creation_date=creation_date,
            total_views=api_channel.total_views,
            total_subscribers=api_channel.total_subscribers,
            total_videos=api_channel.total_videos,
            last_updated=self.raw_data.last_updated
        )

    def _transform_daily_metrics(self) -> List[DailyMetrics]:
        
        return [
            DailyMetrics(
            fetch_date= date.strptime(stat.date, "%Y-%m-%d"),
            views = stat.views,
            subscribers_gained= stat.subs_gained
        )
            for stat in self.raw_data.daily_stats
        ]

    
    def _transform_video_metrics(self) -> List[VideoMetrics]:
        """
        Joins all video data in a single table
        """
        
        titles_map = {video.id: video.title for video in self.raw_data.videos_metadata}
        return [
            VideoMetrics(
                video_id= stat.id,
                title = titles_map.get(stat.id,"Unknown Title"),
                views= stat.views, 
                subscribers_gained= stat.subs_gained
        )
            for stat in self.raw_data.video_stats
        ]



        

