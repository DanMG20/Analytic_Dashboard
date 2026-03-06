from api.youtube_analytics import YouTubeAnalytics 
from api.youtube_data import YouTubeData
from models.raw_data import RawData 
from datetime import date

class DataBuilder:

    def __init__(self, 
                 yt_data: YouTubeData, 
                 yt_analytics :YouTubeAnalytics
                 ):
        self.yt_data = yt_data
        self.yt_analytics = yt_analytics 



    def build(self, start_date: date, end_date : date) -> RawData:
        """ Joins all the data in a single object. """
        videos_metadata = self.yt_data.get_all_videos_metadata()
        video_ids = [v.id for v in videos_metadata]
        return RawData(
            channel_data= self.yt_data.get_channel_data(),
            videos_metadata = videos_metadata,
            daily_stats = self.yt_analytics.get_daily_stats(start_date,end_date),
            video_stats = self.yt_analytics.get_video_stats(start_date,end_date,video_ids)
        )