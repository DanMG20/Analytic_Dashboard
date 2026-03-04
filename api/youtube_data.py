from typing import Any, Optional
from models.channel_info import ChannelInfo
from api.youtube_auth import YoutubeAuth
from utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeData:
    """
    Responsible to interact with Youtube Data API v3.
    """


    def __init__(self, auth_client: YoutubeAuth):
        """
        Initializes the service using an authenticated client.
        """
        self.service = auth_client.get_service("youtube","v3")


    def get_channel_info(self) -> Optional[ChannelInfo]:
        """
        Fetches channel info and returns a validated ChannelInfo object.

        Returns:
            Optional[ChannelInfo]: The validated data or None if not found.
        """
        response = self._request_channel_data()

        item = response.get(["items"][0],[])
        if not item:
            logger.warning("No channel data found for the authenticated user.")
            return None
        logger.info("YT Data Info succesfully obtained")
        return self._map_channel_info(item)


    def _request_channel_data(self) -> dict:
        """
        Executes the raw request to YouTube API.
        """
        return self.service.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        ).execute()

    def _map_channel_info(self,item: dict[str]) -> ChannelInfo:
        """
        Maps the raw API JSON to a ChannelInfo model.
        """
        snippet = item["snippet"]
        stats = item["statistics"]
        content = item["contentDetails"]
        related = content["relatedPlaylists"]

        return ChannelInfo(
            id= item["id"],
            name = snippet["title"],
            creation_date=snippet["publishedAt"],
            total_views=int(stats["viewCount"]),
            total_suscribers=int(stats["subscriberCount"]),
            total_videos= int(stats["videoCount"]),
            uploads_playlist_id = related["uploads"]
        )
