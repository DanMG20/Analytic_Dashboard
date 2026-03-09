# services/dashboard_provider.py
import pandas as pd
from database.repository import YoutubeRepository
from models.dashboard_data import DashboardViewModel

class DashboardDataProvider:
    """
    Bridge between persistence and UI. Handles business/presentation logic
    like transforming domain models into DataFrames.
    """
    
    def __init__(self, repository: YoutubeRepository):
        self.repository = repository

    def build_view_model(self) -> DashboardViewModel:
        # 1. Obtenemos los modelos de dominio (Pydantic) puros
        stats_model, daily_models, video_models = self.repository.get_all_dashboard_data()

        # 2. Lógica de presentación: Convertir Pydantic a Pandas
        stats_df = pd.DataFrame([stats_model.model_dump()]) if stats_model else pd.DataFrame()
        
        daily_df = pd.DataFrame([m.model_dump() for m in daily_models])
        if not daily_df.empty:
            daily_df['fetch_date'] = pd.to_datetime(daily_df['fetch_date']).dt.date
            
        videos_df = pd.DataFrame([m.model_dump() for m in video_models])

        # 3. Retornamos el DTO listo para la UI
        return DashboardViewModel(
            channel_stats=stats_df,
            daily_metrics=daily_df,
            top_videos=videos_df
        )