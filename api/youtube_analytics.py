from api.youtube_auth import YoutubeAuth
from utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeAnalytics:
    """
    Responsible to get Channel info
    """


    def __init__(self):
    
        self.service = YoutubeAuth().get_service("youtube","v3")


    def get_channel_info(self):
        response = self._request_channel_data()


        item = response["items"][0]
        logger.info("Info succesfully obtained")
        return self._map_channel_info(item)


    def _request_channel_data(self):
        return self.service.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        ).execute()

    def _map_channel_info(self, item):
        return {
            "channel_id": item["id"],
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"],
            "total_views": item["statistics"]["viewCount"],
            "total_subscribers": item["statistics"]["subscriberCount"],
            "total_videos": item["statistics"]["videoCount"],
            "videos_list": item["contentDetails"]["relatedPlaylists"]["uploads"]
        }
    

