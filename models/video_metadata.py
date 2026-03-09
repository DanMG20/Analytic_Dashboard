from pydantic import BaseModel

class VideoMetadata(BaseModel):
    """
    Represents the basic metadata of a video asset.
    
    Attributes:
        id: The unique YouTube identifier for the video.
        title: The display title of the video.
    """
    id: str
    title: str