from pydantic import BaseModel

class DailyStats(BaseModel):
    """
    Represents performance metrics for a single day.

    """

    date : str
    views : int
    subs_gained : int
    avg__view_duration: int  