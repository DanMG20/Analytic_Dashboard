# -*- coding: utf-8 -*-

import os
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

class YoutubeConnector: 
    def __init___(self, client_secret, token_file, scopes): 
        self.client_secret = client_secret
        self.token_file = token_file
        self.scopes = scopes
        self.credentials = self.authenticate()
        self.youtube_data = self.build_service("youtube","v3")
        self.youtube_analytics = self.build_service("youtubeAnalytics", "v2")

        if os.environ.get("ENV") != "production":
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    def authenticate(self):
        """
        Autentica al usuario y gestiona el token para no reautorizar cada vez que se ejecuta. 
        """
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
            # --- Intentar cargar credenciales guardadas ---
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

        # --- Si no existen o expiran, pedirlas nuevamente ---
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secret, self.scopes
                )
                creds = flow.run_local_server(port=0)
            # Guardar credenciales para el futuro
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        return creds 


    def build_service(self, api_name, version): 
        from googleapiclient.discovery import build
        return build(api_name, version, credentials= self.credentials)

    def conectar_yt_data():


            # --- Crear cliente con credenciales cargadas ---
        youtube_data_API = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=creds
        )
        return youtube_data_API


    def obtener_parametros_principales(conexion_yt_data_API): 
        """
        Obtiene los parametros principales del canal de Youtube: 
        -Channel ID 
        -Uploads ID playlist
        -Channel Date Creation
        -Total Upload Videos

        regresa un diccionario "parametros_principales" con los parametros listados
        """

        #Solicitud a API
        request = conexion_yt_data_API.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()

        # Parametros 
        channel_id = response["items"][0]["id"]
        upload_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        channel_date_creation = response["items"][0]["snippet"]["publishedAt"]
        total_upload_videos  = response["items"][0]["statistics"]["videoCount"]

        parametros_principales = {
            "channel_id":channel_id,
            "uploads_playlist_id":upload_playlist_id,
            "chanel_date_creation":channel_date_creation,
            "total_upload_videos":total_upload_videos,
        }





conexion_yt_API=YoutubeConnector.conectar_yt_data()
YoutubeConnector.obtener_parametros_principales(conexion_yt_data_API=conexion_yt_API)