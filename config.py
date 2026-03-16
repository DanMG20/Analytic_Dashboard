"""
Global configuration constants for the YouTube Stats Dashboard.
Acts as the Single Source of Truth (SSOT) for the application.
"""

from typing import Final, List

from utils.paths import get_credentials_path

# --- API Authentication ---
SCOPES: Final[List[str]] = ["https://www.googleapis.com/auth/youtube.readonly"]
TOKEN_PATH: Final[str] = str(get_credentials_path("token.pickle"))
CREDENTIALS_PATH: Final[str] = str(get_credentials_path("google_credentials.json"))

# --- YouTube API Client Settings ---
YOUTUBE_API_SERVICE_NAME: Final[str] = "youtube"
YOUTUBE_API_VERSION: Final[str] = "v3"
ANALYTICS_API_SERVICE_NAME: Final[str] = "youtubeAnalytics"
ANALYTICS_API_VERSION: Final[str] = "v2"
# API Limits and Pagination
MAX_RESULTS_PER_PAGE: Final[int] = 50
ANALYTICS_CHUNK_SIZE: Final[int] = 200
# --- Database Settings ---
DB_NAME: Final[str] = "youtube_stats.db"

# --- UI / Dashboard Settings ---
AUTO_SHUTDOWN_TIMEOUT_SECONDS: Final[int] = 3600

# --- Scheduler Settings ---
SCHEDULER_DEFAULT_HOUR: Final[int] = 11
SCHEDULER_DEFAULT_MINUTE: Final[int] = 0
# --- Logger settings ---
LOG_FILE = "dashboard.log"
# Power BI DASHBOARD
POWER_BI_REPORT_URL = "https://app.powerbi.com/groups/me/reports/a6228587-34ec-4661-b947-6ede606f159a/e09839a16a7a8774973a?experience=power-bi"
