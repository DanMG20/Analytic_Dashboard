from database.models import ChannelStats
from datetime import date
from utils.logger import get_logger
logger = get_logger(__name__)

class DataProcessor:
    """Process the data obtained from youtube API's."""

    def __init__(self,data):
        self.data = data

    
    def _process_channel_stats(self):
        channel = self.youtube_data.get_channel_data()
        logger.info("Channel Stats succesfully processed")
        logger.warning(" not sure if date is correct")
        return ChannelStats(
            name = channel.name,
            creation_date=channel.creation_date,
            total_views= channel.total_views,
            total_subscribers= channel.total_subscribers,
            total_videos=channel.total_videos,
            last_updated= date.today()
        )
      
    def _process_daily_metrics(self):
        daily_metrics = self.youtube_analytics.get_daily_stats(init_)


    