from api.youtube_analytics import YouTubeAnalytics 
from api.youtube_data import YouTubeData
from models.raw_data import RawData 
from datetime import date
from utils.logger import get_logger

logger = get_logger(__name__)
class DataBuilder:

    def __init__(self, 
                 yt_data: YouTubeData, 
                 yt_analytics :YouTubeAnalytics
                 ):
        self.yt_data = yt_data
        self.yt_analytics = yt_analytics 



    def build(self, start_date: date, end_date : date) -> RawData:
        """ Joins all the data in a single object. """
        channel_data= self.yt_data.get_channel_data()
        playlist_id = channel_data.uploads_playlist_id
        videos_metadata = self.yt_data.get_all_videos_metadata(playlist_id)
        video_ids = [v.id for v in videos_metadata]
        daily_stats = self.yt_analytics.get_daily_stats(start_date,end_date)
        video_stats = self.yt_analytics.get_video_stats(start_date,end_date,video_ids)
        return RawData(
            channel_data= channel_data,
            videos_metadata = videos_metadata,
            daily_stats = daily_stats,
            video_stats = video_stats,
            last_updated = end_date,
        )