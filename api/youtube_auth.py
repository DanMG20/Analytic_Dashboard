import os
import pickle
from typing import Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from config import CREDENTIALS_PATH, SCOPES, TOKEN_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


class YoutubeAuth:
    """
    Handles Google API credentials lifecycle (Load, Login, Refresh, Save).
    """

    def __init__(self):
        self.credentials: Credentials = self._authenticate()

    def get_service(self, service_name: str, version: str) -> Resource:
        """
        Builds a Google API service resource.
        """
        return build(
            serviceName=service_name, version=version, credentials=self.credentials
        )

    def _authenticate(self) -> Credentials:
        creds = self._load_token()

        if creds and creds.valid:
            return creds

        if creds and creds.expired and creds.refresh_token:
            try:
                creds = self._refresh_token(creds)
            except RefreshError as e:
                logger.warning(f"Refresh failed: {e}. Starting login.")
                creds = self._login()
        else:
            creds = self._login()

        self._save_token(creds)
        return creds

    def _load_token(self) -> Optional[Credentials]:
        if not os.path.exists(TOKEN_PATH):
            return None

        try:
            with open(TOKEN_PATH, "rb") as token:
                return pickle.load(token)
        except (pickle.UnpicklingError, EOFError):
            logger.error("Token file corrupted. Manual login required.")
            return None

    def _refresh_token(self, creds: Credentials) -> Credentials:
        creds.refresh(Request())
        logger.info("Google token refreshed successfully.")
        return creds

    def _login(self) -> Credentials:
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(f"Secrets not found at: {CREDENTIALS_PATH}")

        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(
            port=0,
            host="localhost",
            success_message="Auth complete. You can close this tab.",
        )
        logger.info("Initial Google login successful.")
        return creds

    def _save_token(self, creds: Credentials) -> None:
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
