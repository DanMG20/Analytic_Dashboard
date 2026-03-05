from api.youtube_auth import YoutubeAuth
from api.youtube_data import YouTubeData
from services.data_processor import DataProcessor
from api.youtube_analytics import YouTubeAnalytics
def main():

    youtube_auth = YoutubeAuth()
    youtube_data = YouTubeData(youtube_auth)
    youtube_analytics = YouTubeAnalytics(youtube_auth)

    data_processor = DataProcessor(
        youtube_data=youtube_data,
        youtube_analytics=youtube_analytics
    )
    


if __name__ == "__main__":
    main()