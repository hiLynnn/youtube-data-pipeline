import os
import csv
import argparse
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone


load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def load_artists(input_file):
    """Đọc danh sách artist từ CSV."""
    artists = []

    with open(input_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            artists.append(row)

    return artists


def get_uploads_playlist_id(channel_id):
    """Lấy uploads playlist ID từ YouTube channel ID."""

    url = "https://www.googleapis.com/youtube/v3/channels"

    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("API error:", response.status_code)
        print(response.text)
        return None

    data = response.json()

    if not data.get("items"):
        return None

    return (
        data["items"][0]
        ["contentDetails"]
        ["relatedPlaylists"]
        ["uploads"]
    )


def get_video_ids(playlist_id):
    """
    Lấy tất cả video ID trong playlist.

    Dùng nextPageToken để xử lý pagination.
    """

    video_ids = []
    page_token = None

    while True:

        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": YOUTUBE_API_KEY,
        }

        if page_token:
            params["pageToken"] = page_token

        response = requests.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params=params
        )

        if response.status_code != 200:
            print("API error:", response.status_code)
            print(response.text)
            break

        data = response.json()

        for item in data.get("items", []):

            video_id = (
                item["snippet"]
                ["resourceId"]
                ["videoId"]
            )

            video_ids.append(video_id)

        page_token = data.get("nextPageToken")

        if not page_token:
            break

    return video_ids


def get_video_details(video_ids):
    """
    Lấy thông tin chi tiết video.

    videos.list tối đa 50 video ID/request,
    nên chia thành các batch 50.
    """

    videos = []

    for i in range(0, len(video_ids), 50):

        batch = video_ids[i:i + 50]

        print(
            f"Đang lấy video {i + 1} -> "
            f"{i + len(batch)}"
        )

        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
            "key": YOUTUBE_API_KEY,
        }

        response = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params=params
        )

        if response.status_code != 200:
            print("API error:", response.status_code)
            print(response.text)
            continue

        data = response.json()

        for item in data.get("items", []):

            snippet = item["snippet"]
            statistics = item.get("statistics", {})
            content_details = item.get(
                "contentDetails",
                {}
            )

            video = {
                "video_id": item["id"],
                "video_title": snippet["title"],
                "description": snippet.get("description", ""),
                "channel_id": snippet["channelId"],
                "channel_title": snippet["channelTitle"],
                "published_at": snippet["publishedAt"],
                "duration": content_details.get("duration"),
                "tags": snippet.get("tags", []),
                "category_id": snippet.get("categoryId"),
                "view_count": int(
                    statistics.get("viewCount", 0)
                ),
                "like_count": int(
                    statistics.get("likeCount", 0)
                ),
                "comment_count": int(
                    statistics.get("commentCount", 0)
                ),
            }

            videos.append(video)

    return videos


def save_videos_to_csv(videos, output_file):
    """Lưu video data vào CSV."""

    if not videos:
        print("Không có video để lưu.")
        return

    fieldnames = videos[0].keys()

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(videos)

    print(
        f"Đã lưu {len(videos)} videos vào {output_file}"
    )


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Get YouTube videos from artists"
    )

    parser.add_argument(
        "--input",
        default="data/artists.csv",
        help="Input artists CSV file"
    )

    parser.add_argument(
        "--output",
        default="data/processed/videos.csv",
        help="Output videos CSV file"
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    artists = load_artists(args.input)

    print(f"Đã đọc {len(artists)} artists")
    print("=" * 60)

    extracted_at = datetime.now(timezone.utc)

    all_videos = []

    for artist in artists:

        artist_name = artist["artist_name"]
        channel_id = artist["channel_id"]

        print(f"\nArtist: {artist_name}")
        print(f"Channel ID: {channel_id}")

        if not channel_id:
            print("Không có channel_id")
            continue

        uploads_playlist_id = get_uploads_playlist_id(
            channel_id
        )

        if not uploads_playlist_id:
            print("Không lấy được uploads playlist")
            continue

        print(
            "Uploads playlist:",
            uploads_playlist_id
        )

        video_ids = get_video_ids(
            uploads_playlist_id
        )

        print(
            "Số video IDs:",
            len(video_ids)
        )

        if not video_ids:
            print("Không có video")
            continue

        video_details = get_video_details(
            video_ids
        )

        print(
            "Số video details:",
            len(video_details)
        )

        for video in video_details:

            video["artist_name"] = artist_name
            video["extracted_at"] = extracted_at
            video["source"] = "youtube_api"
            video["ingestion_date"] = extracted_at.date()

        all_videos.extend(video_details)

        if video_details:
            print("Video đầu tiên:")
            print(video_details[0])

        print("-" * 60)

    print("=" * 60)
    print("TỔNG SỐ VIDEO:", len(all_videos))

    save_videos_to_csv(
        all_videos,
        args.output
    )


if __name__ == "__main__":
    main()