from pydantic import BaseModel
from models.channel_info import ChannelInfo
from models.video_info import VideoMetadata
from models.daily_stats import DailyStats
from models.video_stats import VideoStats

class RawData(BaseModel): 
    channel_data : ChannelInfo
    videos_metadata : VideoMetadata
    daily_stats : DailyStats
    video_stats : VideoStats
    
