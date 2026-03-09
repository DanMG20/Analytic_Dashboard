# services/dashboard_provider.py
import pandas as pd
from datetime import date, timedelta
from typing import Tuple
from database.repository import YoutubeRepository
from models.dashboard_data import DashboardViewModel

class DashboardDataProvider:
    """
    Bridge between persistence and UI. Handles presentation logic
    and pre-calculates all necessary metrics for the passive view.
    """
    
    def __init__(self, repository: YoutubeRepository):
        self.repository = repository

    def build_view_model(self) -> DashboardViewModel:
        """Assembles the data and computes metrics for the dashboard."""
        stats_model, daily_models, video_models = self.repository.get_all_dashboard_data()

        stats_df = pd.DataFrame([stats_model.model_dump()]) if stats_model else pd.DataFrame()
        daily_df = pd.DataFrame([m.model_dump() for m in daily_models])
        if not daily_df.empty:
            daily_df['fetch_date'] = pd.to_datetime(daily_df['fetch_date']).dt.date
        videos_df = pd.DataFrame([m.model_dump() for m in video_models])

        curr_views, prev_views, growth, curr_date, prev_date = self._calculate_monthly_growth(daily_df)
        avg_views = self._calculate_average_views(stats_df)

        return DashboardViewModel(
            channel_stats=stats_df,
            daily_metrics=daily_df,
            top_videos=videos_df,
            current_month_views=curr_views,
            previous_month_views=prev_views,
            monthly_growth_percentage=growth,
            current_month_date=curr_date,
            previous_month_date=prev_date,
            average_views_per_video=avg_views
        )

    def _calculate_monthly_growth(self, df: pd.DataFrame) -> Tuple[int, int, float, date, date]:
        """Groups data by month and calculates growth percentage."""
        if df.empty:
            return 0, 0, 0.0, date.today(), date.today()

        temp_df = df.copy()
        temp_df['month'] = pd.to_datetime(temp_df['fetch_date']).dt.month
        temp_df['year'] = pd.to_datetime(temp_df['fetch_date']).dt.year

        limit_date = date.today() - timedelta(days=2)
        curr_m, curr_y = limit_date.month, limit_date.year
        prev_date = limit_date.replace(day=1) - timedelta(days=1)
        prev_m, prev_y = prev_date.month, prev_date.year

        v_curr = int(temp_df[(temp_df['month'] == curr_m) & (temp_df['year'] == curr_y)]['views'].sum())
        v_prev = int(temp_df[(temp_df['month'] == prev_m) & (temp_df['year'] == prev_y)]['views'].sum())
        
        growth = (v_curr - v_prev) / v_prev if v_prev > 0 else 0.0

        return v_curr, v_prev, growth, limit_date, prev_date

    def _calculate_average_views(self, stats_df: pd.DataFrame) -> float:
        """Calculates the average views per video."""
        if stats_df.empty:
            return 0.0
        total_views = stats_df.iloc[0]['total_views']
        total_videos = max(stats_df.iloc[0]['total_videos'], 1)
        return float(total_views / total_videos)