import os 
import sys 
from pathlib import Path
from config import APP_NAME
APPDATA_DIR = Path(os.getenv("APPDATA")) / APP_NAME
APPDATA_DIR.mkdir(parents=True, exist_ok=True)

def data_path(relative_path: str) -> Path:
    """
    Returns a path inside the application data directory.
    Used for user data (config, DB, window position, etc).
    """
    return APPDATA_DIR / relative_path


def get_base_dir() -> Path:
    """
    Returns the absolute path of the directory where the app is running.
    Works for both standard Python execution and PyInstaller compiled .exe.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent


def get_credentials_path(filename: str) -> Path:
    """
    Resolves the absolute path for credential files, ensuring the directory exists.
    """
    creds_dir = get_base_dir() / "credentials"
    creds_dir.mkdir(parents=True, exist_ok=True)
    return creds_dir / filename