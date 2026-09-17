import csv
import argparse


def load_csv(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def clean_text(value):
    if not value:
        return ""

    return " ".join(value.split())


def transform_videos(videos):
    transformed = []

    for video in videos:
        row = {
            "video_id": video["video_id"],
            "video_title": clean_text(video["video_title"]),
            "description": clean_text(video["description"]),
            "channel_id": video["channel_id"],
            "channel_title": clean_text(video["channel_title"]),
            "published_at": video["published_at"],
            "duration": video["duration"],
            "tags": video["tags"],
            "category_id": video["category_id"],
            "view_count": int(video["view_count"] or 0),
            "like_count": int(video["like_count"] or 0),
            "comment_count": int(video["comment_count"] or 0),
            "artist_name": clean_text(video["artist_name"]),
            "extracted_at": video["extracted_at"],
            "source": video["source"],
            "ingestion_date": video["ingestion_date"],
        }

        transformed.append(row)

    return transformed


def transform_comments(comments):
    transformed = []

    for comment in comments:
        row = {
            "artist_name": clean_text(comment["artist_name"]),
            "channel_id": comment["channel_id"],
            "video_id": comment["video_id"],
            "comment_id": comment["comment_id"],
            "parent_id": comment["parent_id"] or "",
            "author_name": clean_text(comment["author_name"]),
            "comment_text": clean_text(comment["comment_text"]),
            "published_at": comment["published_at"],
            "updated_at": comment["updated_at"],
            "like_count": int(comment["like_count"] or 0),
            "reply_count": int(comment["reply_count"] or 0),
            "extracted_at": comment["extracted_at"],
            "ingestion_date": comment["ingestion_date"],
        }

        transformed.append(row)

    return transformed


def save_csv(data, output_file):
    if not data:
        print("Không có dữ liệu để lưu.")
        return

    fieldnames = data[0].keys()

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
        writer.writerows(data)

    print(f"Đã lưu {len(data)} rows vào {output_file}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Transform YouTube data"
    )

    parser.add_argument(
        "--videos-input",
        default="data/processed/videos.csv"
    )

    parser.add_argument(
        "--videos-output",
        default="data/processed/videos_transformed.csv"
    )

    parser.add_argument(
        "--comments-input",
        default="data/processed/comments.csv"
    )

    parser.add_argument(
        "--comments-output",
        default="data/processed/comments_transformed.csv"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    print("=" * 60)
    print("TRANSFORM VIDEOS")
    print("=" * 60)

    videos = load_csv(args.videos_input)
    print(f"Số videos: {len(videos)}")

    transformed_videos = transform_videos(videos)

    save_csv(
        transformed_videos,
        args.videos_output
    )

    print("=" * 60)
    print("TRANSFORM COMMENTS")
    print("=" * 60)

    comments = load_csv(args.comments_input)
    print(f"Số comments: {len(comments)}")

    transformed_comments = transform_comments(comments)

    save_csv(
        transformed_comments,
        args.comments_output
    )

    print("=" * 60)
    print("TRANSFORM SUCCESS")
    print("=" * 60)


if __name__ == "__main__":
    main()