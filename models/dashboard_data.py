from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class DashboardViewModel:
    """
    Data Transfer Object containing all pre-fetched data needed by the UI.
    """
    channel_stats: pd.DataFrame
    daily_metrics: pd.DataFrame
    top_videos: pd.DataFrame