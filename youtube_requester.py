

class YoutubeRequester:
    """
    Métodos para requisitar información a YT Data y YT Analitics
    youtube_data = conexion construida con YT Data API 
    youtube_analytics conexión construida con YT Analytics API

    
    """
    def __init__(self, youtube_data, youtube_analytics): 
        self.youtube_data = youtube_data
        self.youtube_analytics = youtube_analytics





    def obtener_parametros_principales(self): 
        """
        Obtiene los parametros principales del canal de Youtube: 
        -Channel ID 
        -Uploads ID playlist
        -Channel Date Creation
        -Total Upload Videos

        regresa un diccionario "parametros_principales" con los parametros listados
        """

        #Solicitud a API
        request = self.youtube_data.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        print("solicitando datos")
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
        print("parametros obtenidos ")
        return parametros_principales


