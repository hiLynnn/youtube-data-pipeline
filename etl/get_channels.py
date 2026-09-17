import os
import csv
import argparse
import requests
from dotenv import load_dotenv


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

# Đọc file .env
# để lấy YOUTUBE_API_KEY thay vì viết API key trực tiếp vào code.
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


# ============================================================
# 2. DANH SÁCH 10 ARTIST
# ============================================================

# Đây là 10 artist đã lấy từ YouTube Charts Vietnam - TOP_VIEWS.
artists = [
    "Jack - J97",
    "Phương Mỹ Chi",
    "DTAP",
    "Quốc Thiên",
    "Dangrangto",
    "buitruonglinh",
    "Quang Hùng MasterD",
    "RPT MCK",
    "Dat G",
    "DONAL",
]


# ============================================================
# 3. TÌM YOUTUBE CHANNEL
# ============================================================

def search_channel(artist_name):
    """
    Tìm YouTube channel dựa trên tên artist.

    YouTube Data API:
        search.list

    Input:
        artist_name
        Ví dụ: "Jack - J97"

    Output:
        {
            "channel_id": "...",
            "channel_title": "..."
        }

    Nếu không tìm thấy channel -> return None
    """

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",

        # Tên artist mà chúng ta muốn tìm
        "q": artist_name,
        "type": "channel",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(url, params=params)

    # Nếu API trả lỗi thì in ra để biết vấn đề nằm ở đâu.
    if response.status_code != 200:
        print("API error:", response.status_code)
        print(response.text)
        return None

    data = response.json()

    # Nếu API không trả về kết quả
    if not data.get("items"):
        return None

    # Lấy kết quả đầu tiên.
    item = data["items"][0]

    return {
        "channel_id": item["id"]["channelId"],
        "channel_title": item["snippet"]["channelTitle"],
    }


# ============================================================
# 4. GHI KẾT QUẢ RA CSV
# ============================================================

def create_artists_csv(output_file):
    """
    Tìm channel cho 10 artist
    rồi ghi kết quả vào file CSV.
    """

    # Mở file để ghi.
    #
    # newline="":
    # tránh xuất hiện dòng trống giữa các dòng CSV trên một số hệ điều hành.
    #
    # encoding="utf-8":
    # đảm bảo lưu được tiếng Việt.
    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # Ghi header của CSV
        writer.writerow([
            "artist_name",
            "channel_id",
            "channel_title"
        ])

        # Lần lượt tìm channel cho từng artist
        for artist in artists:

            print(f"\nĐang tìm channel: {artist}")

            result = search_channel(artist)

            if result:

                # Ghi kết quả vào CSV
                writer.writerow([
                    artist,
                    result["channel_id"],
                    result["channel_title"]
                ])

                print(
                    f"  Channel: {result['channel_title']}"
                )

                print(
                    f"  ID: {result['channel_id']}"
                )

            else:

                # Nếu không tìm thấy thì vẫn ghi artist.
                # channel_id và channel_title để trống.
                writer.writerow([
                    artist,
                    "",
                    ""
                ])

                print("  KHÔNG TÌM THẤY CHANNEL")

    print(f"\nĐã tạo file: {output_file}")


# ============================================================
# 5. ARGUMENT PARSER
# ============================================================

def parse_arguments():
    """
    Đọc các argument truyền vào khi chạy command line.

    Ví dụ:

        python etl/get_channels.py

    hoặc:

        python etl/get_channels.py --output data/my_artists.csv
    """

    parser = argparse.ArgumentParser(
        description="Find YouTube channels for artists"
    )

    # Cho phép người dùng chỉ định nơi lưu CSV.
    #
    # Nếu không truyền --output
    # thì mặc định lưu vào data/artists.csv
    parser.add_argument(
        "--output",
        default="data/artists.csv",
        help="Output CSV file path"
    )

    return parser.parse_args()


# ============================================================
# 6. MAIN
# ============================================================

def main():

    # Lấy argument từ command line
    args = parse_arguments()

    # Tạo file CSV
    create_artists_csv(args.output)

if __name__ == "__main__":
    main()