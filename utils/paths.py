import os 
from pathlib import Path



APP_NAME = "Analytic Dashboard"
APPDATA_DIR = Path(os.getenv("APPDATA")) / APP_NAME
APPDATA_DIR.mkdir(parents=True, exist_ok=True)

def data_path(relative_path: str) -> Path:
    """
    Returns a path inside the application data directory.
    Used for user data (config, DB, window position, etc).
    """
    return APPDATA_DIR / relative_path