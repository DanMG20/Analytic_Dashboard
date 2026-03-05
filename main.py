from api.youtube_auth import YoutubeAuth
from api.youtube_data import YouTubeData
from datetime import date  # <- import temporal
from api.youtube_analytics import YouTubeAnalytics
def main():

    youtube_auth = YoutubeAuth()
    youtube_data = YouTubeData(youtube_auth)
    youtube_analytics = YouTubeAnalytics(youtube_auth)
    channel_info = youtube_data.get_channel_info()

    #print(channel_info)

    # DATA API TEST
    #videos_metadata = youtube_data.get_all_videos_info(channel_info.uploads_playlist_id)
    #for video in videos_metadata: 
        #print(video)



    init_date = date.fromisoformat("2021-09-29")
    end_date = date.fromisoformat("2026-02-28")

    # DAILY STATS TEST
    stats_list = youtube_analytics.get_daily_stats(init_date, end_date)
    for day in stats_list:
        print(f"Día: {day.date} | Views: {day.views}")  

    today = date.today()
     # VIDEO STATS TEST

    #video_ids = [v.id for v in videos_metadata]
     
    #video_stats =youtube_analytics.get_video_stats(init_date,today,video_ids)
    
    #for index,video in enumerate(video_stats): 
        #print(f"Index: {index} | Id: {video.id} | Views: {video.views} | Subs: {video.subs_gained}")  

if __name__ == "__main__":
    main()