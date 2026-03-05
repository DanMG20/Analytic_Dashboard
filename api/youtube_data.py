from typing import  Optional
from models.channel_info import ChannelInfo
from models.video_info import VideoInfo
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
        self.uploads_playlist_id = None


    def get_channel_info(self) -> Optional[ChannelInfo]:
        """
        Fetches channel info and returns a validated ChannelInfo object.

        Returns:
            Optional[ChannelInfo]: The validated data or None if not found.
        """
        response = self._request_channel_data()

        items = response.get(["items"][0],[])

        if not items:
            logger.warning("No channel data found for the authenticated user.")
            return None
        
        item = items[0]
        logger.info("YT Data Info succesfully obtained")
        return self._map_channel_info(item)



    def get_all_videos_info(self):
        """

        Fetches all uploaded videos Id and name an returns a validated list of VideoInfo objects.

        """
        data = self._request_all_videos()

        if not data:
            logger.warning("No videos found for the authenticated user.")
            return None
    
        logger.info("VIdeo list succesfully obtained")
        return self._build_video_list(data)


    def _request_all_videos(
            self,
            page_token: str = None,
            acumulated_data: list = None
            ) -> list:
        """
        Request all upload video list to Youtube API.
        """
        if acumulated_data is None: 
            acumulated_data = []

        response = self.service.playlistItems().list(
            part="snippet",
            playlistId = self.uploads_playlist_id,
            pageToken = page_token,
            maxResults = 5,
        ).execute()

        items = response.get("items",[])
        acumulated_data.extend(items)
        next_token =response.get("nextPageToken")
        
        if next_token: 
            return self._request_all_videos(
                page_token=next_token,
                acumulated_data=acumulated_data
                )
        else: 
            return acumulated_data

    

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
        self.uploads_playlist_id = related["uploads"]

        return ChannelInfo(
            id= item["id"],
            name = snippet["title"],
            creation_date=snippet["publishedAt"],
            total_views=int(stats["viewCount"]),
            total_suscribers=int(stats["subscriberCount"]),
            total_videos= int(stats["videoCount"]),     
        )
    


    def _map_video_info(self, video: dict[str]) -> VideoInfo:
        """
        Maps the raw API JSON videos info to a VideoInfo model. 
        """
        Id = video["id"]
        title = video["snippet"]["title"]
        
        return VideoInfo(
            Id= Id,
            title= title
        )

    def _build_video_list(self, videos)-> list[VideoInfo]:
        """
        Builds the list of videos 
        Returns:
            list[VideoInfo]
        """
        data = []
        for video in videos:
            video_info = self._map_video_info(video)
            data.append(video_info)
        return data 