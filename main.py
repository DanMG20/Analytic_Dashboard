from api.youtube_data import YouTubeData

def main():
    yt = YouTubeData()
    channel_info = yt.get_channel_info()

    print(channel_info)

if __name__ == "__main__":
    main()