from datetime import date
from typing import List

from pydantic import BaseModel

from models.channel_info import ChannelInfo
from models.daily_stats import DailyStats
from models.video_metadata import VideoMetadata
from models.video_stats import VideoStats


class RawData(BaseModel):
    """
    Joins all data obtained from Youtube Analytics
    adn Youtube Data into a single object.
    """

    channel_data: ChannelInfo
    videos_metadata: List[VideoMetadata]
    daily_stats: List[DailyStats]
    video_stats: List[VideoStats]
    last_updated: date
