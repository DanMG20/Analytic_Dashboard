import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from utils.logger import get_logger
from config import (TOKEN_PATH,CREDENTIALS_PATH,SCOPES)



logger = get_logger(__name__)
class YoutubeAuth: 
    """
    Its responsability is to handle autentication with Youtube Data or Analytics
    """

    def __init__(self):
        self.credentials = self._authenticate()


    def get_service(self,serviceName, version): 
        return build(
            serviceName=serviceName, 
            version=version, 
            credentials=self.credentials)

    def _authenticate(self):
        creds = self._load_token()

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds = self._refresh_token(creds)
            else: 
                creds = self._login()

            self._save_token(creds)

        return creds

    def _load_token(self):
        if not os.path.exists(TOKEN_PATH):
            return None

        with open(TOKEN_PATH, "rb") as token:
            return pickle.load(token)

    def _refresh_token(self, creds):
            creds.refresh(Request())
            logger.info("Token refreshed")
            return creds

    def _login(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH,
            SCOPES
        )
        creds = flow.run_local_server(port=8000)
        logger.info("Successful Google login")
        return creds

    def _save_token(self, creds):
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
