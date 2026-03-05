from api.youtube_auth import YoutubeAuth
from api.youtube_data import YouTubeData
from datetime import date  # <- import temporal
from api.youtube_analytics import YouTubeAnalytics
def main():

    youtube_auth = YoutubeAuth()
    youtube_data = YouTubeData(youtube_auth)
    youtube_analytics = YouTubeAnalytics(youtube_auth)
    #channel_info = youtube_data.get_channel_info()
    #print(channel_info)

    init_date = date.fromisoformat("2026-02-01")
    end_date = date.fromisoformat("2026-02-28")
    stats_list = youtube_analytics.get_daily_stats(init_date, end_date)

    for day in stats_list:
        print(f"Día: {day.date} | Views: {day.views}")
if __name__ == "__main__":
    main()