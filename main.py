from youtube_conector import YoutubeConnector
from youtube_requester import YoutubeRequester

#Direcciones 
CLIENT_SECRET="credenciales/credenciales_google.json"
TOKEN_FILE="credenciales/token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


def main():

    #Paso 1 Conexion

    #Pasamos los datos del cliente mediante un objeto conexion 
    conexion = YoutubeConnector(
        client_secret=CLIENT_SECRET,
        token_file=TOKEN_FILE,
        scopes=SCOPES,
        env ="development"
    )
    #autentica los datos 
    conexion.authenticate()

    #Paso 2 Requisición de datos 
    #creamos el objeto que nos va a solicitar los datos de cualquiera de las dos apis
    requisitor = YoutubeRequester(youtube_analytics=conexion.youtube_analytics,youtube_data=conexion.youtube_data)

    print(requisitor.obtener_parametros_principales())





if __name__ == "__main__": 
    main()