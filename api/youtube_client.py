import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class YouTubeClient:
    
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

    def __init__(self):
        self.credentials = self._authenticate()
        self.service = build("youtube", "v3", credentials=self.credentials)


    
    def _authenticate(self):
        creds = None 

        if os.path.exists("token.pickle"): 
            with open("tocken.pickle", "rb") as token: 
                creds = pickle.load(token)

        if not creds or not creds.valid: 
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials/google_credentials.json",
                    self.SCOPES
                )
                creds = flow.run_local_server(port = 8000)

            with open ("tocken.pickle", "wb") as token: 
                pickle.dump(creds, token)

        return creds 
    


    def get_my_channel_info(self): 

        request = self.service.channels().list(
            part ="snippet,statistics",
            mine = True
        )
        return request.exectute()