from dataclasses import dataclass
from datetime import date
import pandas as pd

@dataclass(frozen=True)
class DashboardViewModel:
    """
    Data Transfer Object containing all pre-fetched and pre-calculated data needed by the UI.
    Uses native dataclasses instead of Pydantic to support Pandas DataFrames natively.
    """
    channel_stats: pd.DataFrame
    daily_metrics: pd.DataFrame
    top_videos: pd.DataFrame
    
    # Pre-calculated metrics for the UI
    current_month_views: int
    previous_month_views: int
    monthly_growth_percentage: float
    current_month_date: date
    previous_month_date: date
    average_views_per_video: float