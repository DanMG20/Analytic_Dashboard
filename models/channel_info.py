from pydantic import BaseModel


class ChannelInfo(BaseModel):
    """
    Represents the data contract for a YouTube channel.

    Attributes:
        channel_id: Unique identifier of the channel.
        title: Display name of the channel.
        published_at: ISO 8601 creation date.
        total_views: Lifetime view count.
        total_subscribers: Current subscriber count.
        total_videos: Number of public videos uploaded.
        uploads_playlist_id: ID of the playlist containing uploads.
    """

    id: str
    name: str
    creation_date: str
    total_views: int
    total_subscribers: int
    total_videos: int
    uploads_playlist_id: str
