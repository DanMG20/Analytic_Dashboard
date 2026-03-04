from api.youtube_auth import YoutubeAuth
from utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeAnalytics:
    """
    Responsible to get info from Youtube Analytics 
    """


    def __init__(self):
    
        self.service = YoutubeAuth().get_service("youtubeAnalytics","v2")


    def _request_data(self):
        response = self._request_channel_data()


        item = response["items"][0]
        logger.info("Info succesfully obtained")
        return item


    def _request_channel_data(self):
        return self.service.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        ).execute()
    

