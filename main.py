from api.youtube_auth import YoutubeAuth
from api.youtube_data import YouTubeData
from api.data_builder import DataBuilder
from datetime import date 
from services.data_processor import DataProcessor
from api.youtube_analytics import YouTubeAnalytics
def main():
    youtube_auth = YoutubeAuth()
    yt_data = YouTubeData(youtube_auth)
    yt_analytics = YouTubeAnalytics(youtube_auth)
    data_builder = DataBuilder(yt_data,yt_analytics)


    

    #Se dispara scheduler 
    # scheduler dispara comparacion de fechas -> retorna fecha de inicio
    start_date = "2024-01-01" 
    end_date = date.today()

    #4.- > se realiza la requisición de fechas 
    raw_data = data_builder.build(start_date,end_date)


    data_processor = DataProcessor(
        youtube_data=yt_data,
        youtube_analytics=yt_analytics
    )
    
    data_processor._process_channel_stats()


    """
    Flujo basico, 

    1.- Inicio
    2.- se dispara scheduler
    3.- scheduler dispara la comparación de fechas



    4.- se realiza la requisición de informacion a la API Listo 

    5.- se procesa la información requisitada en data processor
    6.-la información requisitada en data processor se inyecta a la db mediante el repo
    7.- Fin

    """



if __name__ == "__main__":
    main()