from api.youtube_auth import YoutubeAuth
from api.youtube_data import YouTubeData
from api.youtube_analytics import YouTubeAnalytics
def main():

    youtube_auth = YoutubeAuth()
    youtube_data = YouTubeData(youtube_auth)
    youtube_analytics = YouTubeAnalytics()
    channel_info = youtube_data.get_channel_info()
    print(channel_info)
    #analytics = youtube_analytics._request_data()
if __name__ == "__main__":
    main()