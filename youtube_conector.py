import os
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

class YoutubeConnector: 
    def __init__(self, client_secret, token_file, scopes, env="development"): 
        self.client_secret = client_secret
        self.token_file = token_file
        self.scopes = scopes
        self.env = env
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
            print("Intentando Cargar Credenciales")

        # --- Si no existen o expiran, pedirlas nuevamente ---
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())

            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secret, self.scopes
                )
                print("Es necesario autenticar en el navegador")
                creds = flow.run_local_server(port=0)
            # Guardar credenciales para el futuro
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        return creds 


    def build_service(self, api_name, version): 
        from googleapiclient.discovery import build
        print("Construyendo servicio")
        return build(api_name, version, credentials= self.credentials)































