from datetime import date
from typing import Any, Dict, List

from googleapiclient.errors import HttpError

from api.youtube_auth import YoutubeAuth
from config import (ANALYTICS_API_SERVICE_NAME, ANALYTICS_API_VERSION,
                    ANALYTICS_CHUNK_SIZE)
from models.daily_stats import DailyStats
from models.video_stats import VideoStats
from utils.logger import get_logger
from utils.retry import api_retry

logger = get_logger(__name__)


class YouTubeAnalytics:
    """Gateway to interact with YouTube Analytics API v2."""

    def __init__(self, auth_client: YoutubeAuth):
        self.service = auth_client.get_service(
            ANALYTICS_API_SERVICE_NAME, ANALYTICS_API_VERSION
        )

    def get_daily_stats(self, start_date: date, end_date: date) -> List[DailyStats]:
        """Fetches historical channel data."""
        try:
            response = self._fetch_daily_report(start_date, end_date)
            rows = response.get("rows", [])
            return [self._map_daily_row(row) for row in rows]
        except HttpError as error:
            logger.error(f"API Error fetching daily stats: {error}")
            return []

    def get_video_stats(
        self, start_date: date, end_date: date, video_ids: List[str]
    ) -> List[VideoStats]:
        """
        Fetches stats for ALL provided video IDs.
        Ensures the output list matches the input list size (Zero-filling).
        """
        if not video_ids:
            return []

        raw_results_map = self._fetch_all_batches_as_map(
            start_date, end_date, video_ids
        )

        final_stats = []
        for vid_id in video_ids:
            stats = raw_results_map.get(
                vid_id, VideoStats(id=vid_id, views=0, subs_gained=0)
            )
            final_stats.append(stats)

        logger.info(
            f"Final reconciliation complete: {len(final_stats)} videos processed."
        )
        return final_stats

    def _fetch_all_batches_as_map(
        self, start: date, end: date, video_ids: List[str]
    ) -> Dict[str, VideoStats]:
        """Fetches all batches and returns a dictionary for fast lookup."""
        results_map: Dict[str, VideoStats] = {}
        chunks = [
            video_ids[i : i + ANALYTICS_CHUNK_SIZE]
            for i in range(0, len(video_ids), ANALYTICS_CHUNK_SIZE)
        ]

        for chunk in chunks:
            try:
                batch_rows = self._fetch_video_batch(start, end, chunk)
                for row in batch_rows:
                    stats = self._map_video_row(row)
                    results_map[stats.id] = stats
            except HttpError as error:
                logger.error(f"Error in batch request: {error}")

        return results_map

    @api_retry
    def _fetch_video_batch(
        self, start: date, end: date, ids: List[str]
    ) -> List[List[Any]]:
        """Queries metrics for a specific set of video IDs."""
        id_filter = ",".join(ids)
        response = (
            self.service.reports()
            .query(
                ids="channel==MINE",
                startDate=start.isoformat(),
                endDate=end.isoformat(),
                dimensions="video",
                metrics="views,subscribersGained",
                filters=f"video=={id_filter}",
            )
            .execute()
        )

        return response.get("rows", [])

    @api_retry
    def _fetch_daily_report(self, start: date, end: date) -> Dict[str, Any]:
        return (
            self.service.reports()
            .query(
                ids="channel==MINE",
                startDate=start.isoformat(),
                endDate=end.isoformat(),
                metrics="views,subscribersGained,averageViewDuration",
                dimensions="day",
                sort="day",
            )
            .execute()
        )

    def _map_daily_row(self, row: List[Any]) -> DailyStats:
        return DailyStats(
            date=row[0],
            views=int(row[1]),
            subs_gained=int(row[2]),
            avg_view_duration=int(row[3]),
        )

    def _map_video_row(self, row: List[Any]) -> VideoStats:
        return VideoStats(id=str(row[0]), views=int(row[1]), subs_gained=int(row[2]))
