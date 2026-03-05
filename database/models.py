from datetime import date
from pydantic import BaseModel, Field, ConfigDict


class ChannelStats(BaseModel):
    """
    Represents the global state and metadata of a YouTube channel.
    """
    model_config = ConfigDict(from_attributes=True)

    name: str
    creation_date: date
    total_views: int = Field(ge=0)
    total_subscribers: int = Field(ge=0)
    total_videos: int = Field(ge=0)
    last_updated: date = Field(default_factory=date.today)


class DailyMetrics(BaseModel):
    """
    Represents historical daily performance metrics.
    """
    model_config = ConfigDict(from_attributes=True)

    fetch_date: date
    views: int = Field(ge=0)
    subscribers_gained: int


class VideoMetrics(BaseModel):
    """
    Represents performance metrics for individual video assets.
    """
    model_config = ConfigDict(from_attributes=True)

    video_id: str
    title: str
    views: int = Field(ge=0)
    subscribers_gained: int