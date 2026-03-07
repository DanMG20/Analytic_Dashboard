import sqlite3
from typing import List, Optional
from database.connection import DatabaseManager
from datetime import date
from database.models import ChannelStats, DailyMetrics, VideoMetrics
from database.migrations import run_migrations
from utils.logger import get_logger

logger = get_logger(__name__)



class YoutubeRepository:
    """
    Handles persistence logic for Youtube metrics into SQLite.
    """

    def __init__(self,db_manager : DatabaseManager):
        self.db = db_manager
        run_migrations(self.db)

    def get_last_updated_date(self) -> Optional[date]: 

        try: 
            with self.db.get_connection() as conn: 
                return self._get_last_updated_date(conn)
        except Exception as e: 
            logger.error(f"Failed to get last updated date {e}")
            raise

    
    def _get_last_updated_date(self,conn: sqlite3.Connection) ->date:


        query = """
        SELECT last_updated FROM channel_stats 
        """
        cursor = conn.execute(query)
        last_update = cursor.fetchone()
        if last_update:
            return last_update[0]
        return None
        
    def save_all(
            self, 
            stats: ChannelStats,
            daily: List[DailyMetrics],
            videos : List[VideoMetrics]
            ):
        """ Main entry point to persist all processed data in a single transaction"""

        try:
            with self.db.get_connection() as conn:
                self._upsert_channel_stats(conn, stats)
                self._upsert_daily_metrics(conn, daily)
                self._upsert_video_metrics(conn, videos)
        
        except Exception as e:
            logger.error(f" Failed to save data {e}")
            raise




    def _upsert_channel_stats(
            self, 
            conn : sqlite3.Connection,
            stats : ChannelStats):  
        query= """
        INSERT OR REPLACE INTO channel_stats
        (name, 
        creation_date, 
        total_views, 
        total_subscribers, 
        total_videos, 
        last_updated)
        VALUES (?,?,?,?,?,?)
        """
        conn.execute(query, (
            stats.name,
            stats.creation_date, 
            stats.total_views,
            stats.total_subscribers,
            stats.total_videos,
            stats.last_updated
        ))
            
    def _upsert_daily_metrics(
            self,
            conn: sqlite3.Connection,
            metrics : List[DailyMetrics]):

        query = """
        INSERT OR REPLACE INTO daily_metrics
        (fetch_date,
        views,
        subscribers_gained)
        VALUES (?,?,?)
        """
        data = [(
            metric.fetch_date, 
            metric.views, 
            metric.subscribers_gained) 
            for metric in metrics]
        conn.executemany(query, data)

    def _upsert_video_metrics(
            self,
            conn: sqlite3.Connection,
            metrics : List[VideoMetrics]
            ): 
        query = """
        INSERT OR REPLACE INTO video_metrics 
        (video_id,
        title,
        views,
        subscribers_gained)
        VALUES (?,?,?,?)
        """
        data = [(
            metric.video_id,
            metric.title,
            metric.views,
            metric.subscribers_gained,
        )
        for metric in metrics]
        conn.executemany(query,data)
          