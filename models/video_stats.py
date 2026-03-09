from pydantic import BaseModel


class VideoStats(BaseModel):
    """
    Represents performance metrics for an individual video.

    Attributes:
        id: Unique identifier of the video.
        views: Total views acquired in the specified period.
        subs_gained: Subscribers gained from this video in the period.
    """

    id: str
    views: int
    subs_gained: int
