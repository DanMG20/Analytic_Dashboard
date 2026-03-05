from datetime import date
from pydantic import BaseModel, Field, ConfigDict

"""
Definición de los modelos de datos para el sistema de estadísticas.
Estos modelos validan la información antes de ser procesada o guardada.
"""

class ChannelStats(BaseModel): 
    """
    Información general y estado actual del canal.
    """
    model_config = ConfigDict(from_attributes=True)

    name: str
    creation_date: date  # Pydantic lo validará aunque SQLite lo guarde como texto
    total_views: int = Field(ge=0)
    total_subscribers: int = Field(ge=0)
    total_videos: int = Field(ge=0)
    last_updated: date = Field(default_factory=date.today)


class DailyMetrics(BaseModel):
    """
    Métricas diarias históricas para análisis de tendencias.
    """
    model_config = ConfigDict(from_attributes=True)

    fetch_date: date
    views: int = Field(ge=0) # Cambiado a int para permitir cálculos estadísticos
    subscribers_gained: int


class VideoMetrics(BaseModel):
    """
    Métricas específicas por cada video subido.
    """
    model_config = ConfigDict(from_attributes=True)

    video_id: str
    title: str
    views: int = Field(ge=0)
    subscribers_gained: int