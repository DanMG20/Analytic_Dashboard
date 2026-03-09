from typing import Optional, List, Dict, Any
from utils.retry import api_retry
from googleapiclient.errors import HttpError

from api.youtube_auth import YoutubeAuth
from models.channel_info import ChannelInfo
from models.video_metadata import VideoMetadata
from utils.logger import get_logger

logger = get_logger(__name__)

class YouTubeData:
    """Gateway to interact with YouTube Data API v3."""

    def __init__(self, auth_client: YoutubeAuth):
        """Initializes the service using an authenticated client."""
        self.service = auth_client.get_service("youtube", "v3")

    def get_channel_data(self) -> Optional[ChannelInfo]:
        """Fetches channel info and its uploads playlist ID."""
        try:
            response = self._request_channel_data()
            items = response.get("items", [])

            if not items:
                logger.warning("No channel data found.")
                return None

            logger.info("Channel info successfully obtained.")
            return self._map_channel_info(items[0])
        except (HttpError, KeyError, IndexError) as error:
            logger.error(f"Error fetching channel info: {error}")
            return None

    def get_all_videos_metadata(self, playlist_id: str) -> Optional[List[VideoMetadata]]:
        """
        Fetches all videos from a specific playlist.
        Args:
            playlist_id: The ID of the 'uploads' playlist.
        """
        try:
            raw_videos = self._fetch_all_playlist_items(playlist_id)
            if not raw_videos:
                logger.warning("No videos found in playlist.")
                return None

            return [self._map_video_info(item) for item in raw_videos]
        except HttpError as error:
            logger.error(f"Error fetching video list: {error}")
            return None

    @api_retry
    def _request_channel_data(self) -> Dict[str, Any]:
        """Raw request for channel statistics and content details."""
        return self.service.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        ).execute()

    def _fetch_all_playlist_items(self, playlist_id: str) -> List[Dict[str, Any]]:
        """Iteratively fetches all items from a playlist using page tokens."""
        all_items: List[Dict[str, Any]] = []
        next_page_token: Optional[str] = None

        while True:
            response = self._request_one_page_items(playlist_id,next_page_token)

            all_items.extend(response.get("items", []))
            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break
        
        return all_items
    

    @api_retry
    def _request_one_page_items(
            self, 
            playlist_id: str , 
            next_page_token : Optional[str]
            ) -> Dict[str, Any]:
            
        return  (self.service.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                pageToken=next_page_token,
                maxResults=50
            ).execute())

    def _map_channel_info(self, item: Dict[str, Any]) -> ChannelInfo:
        """Maps raw API JSON to ChannelInfo and extracts internal metadata."""
        snippet = item["snippet"]
        stats = item["statistics"]
        uploads_id = item["contentDetails"]["relatedPlaylists"]["uploads"]

        return ChannelInfo(
            id=item["id"],
            name=snippet["title"],
            creation_date=snippet["publishedAt"],
            total_views=int(stats["viewCount"]),
            total_subscribers=int(stats["subscriberCount"]),
            total_videos=int(stats["videoCount"]),
            uploads_playlist_id=uploads_id 
        )

    def _map_video_info(self, item: Dict[str, Any]) -> VideoMetadata:
        """Maps raw API JSON playlist item to VideoInfo model."""
        return VideoMetadata(
            id=item["contentDetails"]["videoId"],
            title=item["snippet"]["title"]
        )