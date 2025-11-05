# -*- coding: utf-8 -*-

import os
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "credenciales/credenciales_google.json"
    token_file = "credenciales/token.json"  # aquí guardaremos el acceso

    creds = None

    # --- Intentar cargar credenciales guardadas ---
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # --- Si no existen o expiran, pedirlas nuevamente ---
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Guardar credenciales para el futuro
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    # --- Crear cliente con credenciales cargadas ---
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=creds
    )

    # --- Ejemplo: obtener canal y playlist de subidas ---
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    )
    response = request.execute()

    channel_id = response["items"][0]["id"]
    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    print(f"Channel ID: {channel_id}")
    print(f"Uploads Playlist ID: {uploads_playlist_id}")

if __name__ == "__main__":
    main()
