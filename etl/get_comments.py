import os
import csv
import argparse
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone


load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def load_videos(input_file):
    """Đọc danh sách video từ CSV."""

    videos = []

    with open(input_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            videos.append(row)

    return videos


def get_comments(video_id, artist_name, channel_id, extracted_at):
    """Lấy tất cả top-level comments của một video."""

    comments = []
    page_token = None

    while True:

        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": 100,
            "key": YOUTUBE_API_KEY,
        }

        if page_token:
            params["pageToken"] = page_token

        response = requests.get(
            "https://www.googleapis.com/youtube/v3/commentThreads",
            params=params
        )

        if response.status_code == 403:
            print(f"  Comments bị tắt: {video_id}")
            break

        if response.status_code != 200:
            print("  API error:", response.status_code)
            print(response.text)
            break

        data = response.json()

        for item in data.get("items", []):

            comment = item["snippet"]["topLevelComment"]
            snippet = comment["snippet"]

            comment_record = {
                "artist_name": artist_name,
                "channel_id": channel_id,
                "video_id": video_id,
                "comment_id": comment["id"],
                "parent_id": None,
                "author_name": snippet.get(
                    "authorDisplayName", ""
                ),
                "comment_text": snippet.get(
                    "textOriginal", ""
                ),
                "published_at": snippet["publishedAt"],
                "updated_at": snippet["updatedAt"],
                "like_count": int(
                    snippet.get("likeCount", 0)
                ),
                "reply_count": int(
                    item["snippet"].get(
                        "totalReplyCount", 0
                    )
                ),
                "extracted_at": extracted_at,
                "ingestion_date": extracted_at.date(),
            }

            comments.append(comment_record)

        page_token = data.get("nextPageToken")

        if not page_token:
            break

    return comments


def save_comments_to_csv(comments, output_file):
    """Lưu comments vào CSV."""

    if not comments:
        print("Không có comment để lưu.")
        return

    fieldnames = comments[0].keys()

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
        writer.writerows(comments)

    print(
        f"Đã lưu {len(comments)} comments vào {output_file}"
    )


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Get YouTube comments"
    )

    parser.add_argument(
        "--input",
        default="data/processed/videos.csv",
        help="Input videos CSV file"
    )

    parser.add_argument(
        "--output",
        default="data/processed/comments.csv",
        help="Output comments CSV file"
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    videos = load_videos(args.input)

    print(f"Đã đọc {len(videos)} videos")
    print("=" * 60)

    extracted_at = datetime.now(timezone.utc)

    # Lấy tối đa 10 video cho mỗi artist
    selected_videos = []

    artist_counts = {}

    for video in videos:

        artist_name = video["artist_name"]

        if artist_counts.get(artist_name, 0) >= 10:
            continue

        selected_videos.append(video)
        artist_counts[artist_name] = (
            artist_counts.get(artist_name, 0) + 1
        )

    print("Số artist:", len(artist_counts))
    print("Số video sẽ lấy comments:", len(selected_videos))
    print("=" * 60)

    all_comments = []

    for index, video in enumerate(selected_videos, start=1):

        video_id = video["video_id"]
        artist_name = video["artist_name"]
        channel_id = video["channel_id"]

        print(
            f"[{index}/{len(selected_videos)}] "
            f"{artist_name} - {video_id}"
        )

        comments = get_comments(
            video_id,
            artist_name,
            channel_id,
            extracted_at
        )

        all_comments.extend(comments)

        print(
            f"  Comments: {len(comments)}"
        )

    print("=" * 60)
    print("TỔNG SỐ COMMENTS:", len(all_comments))

    save_comments_to_csv(
        all_comments,
        args.output
    )

if __name__ == "__main__":
    main()