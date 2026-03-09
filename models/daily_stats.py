from pydantic import BaseModel

class DailyStats(BaseModel):
    """
    Represents performance metrics for a single day.

    Attributes:
    date: date of the collected data.
    views: Total views acquired in that day.
    subs_gained: Subscribers gained in that day.
    avg_view_duration : average view duration obtained in that day.

    """

    date : str
    views : int
    subs_gained : int
    avg_view_duration: int  