from api.youtube_client import YouTubeClient

def main():
    yt = YouTubeClient()
    channel_info = yt.get_my_channel()

    print(channel_info)

if __name__ == "__main__":
    main()