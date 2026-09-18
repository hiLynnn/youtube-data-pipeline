# YouTube Data Pipeline

## 1. Giới thiệu

Đây là project Data Engineering xây dựng pipeline thu thập dữ liệu từ **YouTube Data API v3**, xử lý dữ liệu bằng **Python**, lưu trữ vào **Google BigQuery** và chạy tự động trên **Google Cloud Compute Engine VM**.

Pipeline được thiết kế theo mô hình:

```text
YouTube Data API
       ↓
    Python
       ↓
    Extract
       ↓
     CSV
       ↓
   Transform
       ↓
 BigQuery
       ↓
Google Cloud VM
       ↓
    Cron Job
```

Project sử dụng dữ liệu của 10 nghệ sĩ/kênh YouTube và thu thập hai nhóm dữ liệu chính:

* Video
* Comment

---

# 2. Mục tiêu project

Project nhằm thực hành một pipeline Data Engineering hoàn chỉnh từ lúc lấy dữ liệu cho đến khi tự động chạy.

Các mục tiêu chính:

* Sử dụng YouTube Data API v3.
* Tìm và xác định channel ID.
* Thu thập danh sách video.
* Thu thập thông tin chi tiết của video.
* Thu thập comments.
* Làm sạch và chuẩn hóa dữ liệu.
* Lưu dữ liệu trung gian dưới dạng CSV.
* Load dữ liệu vào BigQuery.
* Sử dụng schema rõ ràng cho BigQuery.
* Logging quá trình chạy pipeline.
* Quản lý API key và credential an toàn.
* Đưa source code lên GitHub.
* Deploy project lên Google Cloud VM.
* Sử dụng cron để tự động chạy pipeline.

---

# 3. Kiến trúc tổng thể

```text
                    ┌─────────────────────┐
                    │   YouTube Data API  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   get_channels.py   │
                    │ Find Channel IDs     │
                    └──────────┬──────────┘
                               │
                               ▼
                         artists.csv
                               │
                               ▼
                    ┌─────────────────────┐
                    │    get_videos.py    │
                    │ Extract video data  │
                    └──────────┬──────────┘
                               │
                               ▼
                          videos.csv
                               │
                               ▼
                    ┌─────────────────────┐
                    │   get_comments.py   │
                    │ Extract comments    │
                    └──────────┬──────────┘
                               │
                               ▼
                         comments.csv
                               │
                               ▼
                    ┌─────────────────────┐
                    │    transform.py     │
                    │ Clean & transform   │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          videos_transformed.csv  comments_transformed.csv
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │  load_bigquery.py   │
                    │ Load to BigQuery    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      BigQuery       │
                    │                     │
                    │  videos             │
                    │  comments           │
                    └─────────────────────┘
```

---

# 4. Công nghệ sử dụng

| Công nghệ                   | Mục đích                |
| --------------------------- | ----------------------- |
| Python                      | Viết pipeline           |
| YouTube Data API v3         | Thu thập dữ liệu        |
| Requests                    | Gọi REST API            |
| CSV                         | Lưu dữ liệu trung gian  |
| python-dotenv               | Đọc biến môi trường     |
| Google Cloud BigQuery       | Data Warehouse          |
| Google Cloud Compute Engine | Chạy pipeline           |
| Git/GitHub                  | Version control         |
| Linux                       | Môi trường chạy trên VM |
| Cron                        | Scheduling              |
| Python Logging              | Theo dõi pipeline       |

---

# 5. Cấu trúc project

```text
youtube-data-pipeline/
│
├── data/
│   ├── artists.csv
│   └── processed/
│       ├── videos.csv
│       ├── videos_transformed.csv
│       ├── comments.csv
│       └── comments_transformed.csv
│
├── etl/
│   ├── __init__.py
│   ├── get_channels.py
│   ├── get_videos.py
│   ├── get_comments.py
│   ├── transform.py
│   └── load_bigquery.py
│
├── logs/
│   └── pipeline.log
│
├── .env
├── .env.example
├── .gitignore
├── main.py
├── README.md
├── requirements.txt
└── test_ST-MTP.ipynb

Trong GitHub, `.env`, dữ liệu thực tế và log không được commit.

---

# 6. Tư duy thiết kế pipeline

Pipeline được chia thành ba giai đoạn chính:

```text
Extract → Transform → Load
```

Đây là mô hình ETL.

## Extract

Lấy dữ liệu từ YouTube API.

## Transform

Làm sạch và chuẩn hóa dữ liệu.

## Load

Đưa dữ liệu đã xử lý vào BigQuery.

Việc chia pipeline thành các module riêng giúp:

* Dễ đọc code.
* Dễ debug.
* Dễ test từng bước.
* Dễ thay đổi một thành phần mà không ảnh hưởng toàn bộ project.
* Dễ đưa lên server/VM và chạy tự động.

---

# 7. Bước 1 — Xác định các YouTube channel

File:

```text
etl/get_channels.py
```

File này sử dụng YouTube Data API để tìm channel dựa trên tên nghệ sĩ.

Kết quả được lưu vào:

```text
data/artists.csv
```

Ví dụ:

```csv
artist_name,channel_id,channel_title
Jack - J97,UC...,J97
Phương Mỹ Chi,UC...,Phuong My Chi
...
```

## Tại sao cần channel ID?

Tên channel không phải là identifier tốt để lấy dữ liệu.

Ví dụ:

```text
artist_name = "Jack - J97"
```

có thể có nhiều kết quả tìm kiếm.

Trong khi:

```text
channel_id = UCxxxxxxxx
```

là identifier cụ thể của channel.

Vì vậy pipeline sử dụng:

```text
artist_name
      ↓
channel_id
      ↓
YouTube API
```

Sau khi xác định được channel ID, bước này không cần chạy lại trong mỗi lần pipeline chạy.

---

# 8. Bước 2 — Extract videos

File:

```text
etl/get_videos.py
```

Pipeline đọc:

```text
data/artists.csv
```

Sau đó với mỗi channel:

### Bước 1

Lấy `uploads playlist ID`.

YouTube mỗi channel có một playlist chứa các video upload.

### Bước 2

Lấy danh sách video ID từ playlist.

API trả về tối đa 50 item mỗi request nên phải xử lý pagination bằng:

```text
nextPageToken
```

Pipeline tiếp tục request cho đến khi không còn:

```text
nextPageToken
```

### Bước 3

Lấy thông tin chi tiết video.

API sử dụng:

```text
part=snippet,statistics,contentDetails
```

để lấy:

* Title
* Description
* Channel
* Published time
* Duration
* Tags
* Category
* Views
* Likes
* Comments

Dữ liệu được lưu vào:

```text
data/processed/videos.csv
```

---

# 9. Vì sao phải batch video ID?

YouTube API cho phép truyền nhiều video ID trong một request.

Thay vì:

```text
video 1 → request
video 2 → request
video 3 → request
...
```

pipeline gom tối đa 50 ID:

```text
video 1
video 2
...
video 50
       ↓
   1 request
```

Điều này giúp giảm số lượng API request và sử dụng quota hiệu quả hơn.

---

# 10. Bước 3 — Extract comments

File:

```text
etl/get_comments.py
```

Pipeline đọc:

```text
videos.csv
```

Sau đó gọi:

```text
commentThreads.list
```

để lấy comments.

Mỗi request lấy tối đa:

```text
100 comments
```

Nếu còn dữ liệu, API trả về:

```text
nextPageToken
```

Pipeline tiếp tục lấy page tiếp theo.

---

# 11. Giới hạn comments

Comments có thể rất lớn.

Nếu lấy toàn bộ comments của toàn bộ 5.641 videos thì pipeline có thể chạy rất lâu và sử dụng nhiều API quota.

Vì vậy project giới hạn:

```text
10 videos / artist
```

Với 10 artists:

```text
10 × 10 = tối đa 100 videos
```

Điều này vẫn đủ để chứng minh pipeline có khả năng xử lý comments mà không khiến quá trình chạy trở nên quá lớn.

Kết quả thực tế:

```text
Videos:   5,641
Comments: 49,748
```

---

# 12. Xử lý trường hợp video không cho phép comment

Một số video có thể tắt comments.

API có thể trả về:

```text
403
```

Pipeline kiểm tra trường hợp này và bỏ qua video đó thay vì làm toàn bộ pipeline thất bại.

Tư duy xử lý:

```text
Video
  ↓
Comments enabled?
  ├── Yes → lấy comments
  │
  └── No  → bỏ qua video
```

Đây là một phần quan trọng của data pipeline vì dữ liệu thực tế không phải lúc nào cũng đầy đủ.

---

# 13. Bước 4 — Transform

File:

```text
etl/transform.py
```

Input:

```text
videos.csv
comments.csv
```

Output:

```text
videos_transformed.csv
comments_transformed.csv
```

## Các thao tác transform

### Clean text

Ví dụ dữ liệu:

```text
"   Đây   là   một   video   "
```

được chuẩn hóa thành:

```text
"Đây là một video"
```

### Convert numeric fields

Ví dụ:

```text
"12345"
```

được chuyển thành:

```text
12345
```

để BigQuery có thể lưu dưới dạng:

```text
INT64
```

Các trường được xử lý gồm:

```text
view_count
like_count
comment_count
reply_count
```

### Xử lý giá trị rỗng

Ví dụ:

```text
None
""
```

được xử lý phù hợp trước khi load vào BigQuery.

---

# 14. Bước 5 — Load vào BigQuery

File:

```text
etl/load_bigquery.py
```

Dataset:

```text
youtube_analytics
```

Có hai table:

```text
youtube_analytics.videos
youtube_analytics.comments
```

---

# 15. BigQuery schema

## Videos

| Column         | Type      |
| -------------- | --------- |
| video_id       | STRING    |
| video_title    | STRING    |
| description    | STRING    |
| channel_id     | STRING    |
| channel_title  | STRING    |
| published_at   | TIMESTAMP |
| duration       | STRING    |
| tags           | STRING    |
| category_id    | STRING    |
| view_count     | INT64     |
| like_count     | INT64     |
| comment_count  | INT64     |
| artist_name    | STRING    |
| extracted_at   | TIMESTAMP |
| source         | STRING    |
| ingestion_date | DATE      |

## Comments

| Column         | Type      |
| -------------- | --------- |
| artist_name    | STRING    |
| channel_id     | STRING    |
| video_id       | STRING    |
| comment_id     | STRING    |
| parent_id      | STRING    |
| author_name    | STRING    |
| comment_text   | STRING    |
| published_at   | TIMESTAMP |
| updated_at     | TIMESTAMP |
| like_count     | INT64     |
| reply_count    | INT64     |
| extracted_at   | TIMESTAMP |
| ingestion_date | DATE      |

---

# 16. Tại sao sử dụng schema rõ ràng?

Không sử dụng hoàn toàn:

```text
autodetect
```

mà định nghĩa schema trước.

Lý do:

* Kiểm soát data type.
* Tránh BigQuery tự đoán sai kiểu dữ liệu.
* Dễ query.
* Dễ xây dựng data warehouse.
* Dễ phát hiện lỗi dữ liệu.

Ví dụ:

```text
view_count
```

phải là:

```text
INT64
```

thay vì:

```text
STRING
```

---

# 17. Xử lý description có newline

Description của YouTube có thể chứa xuống dòng.

Ví dụ:

```text
Đây là video.

Follow:
Facebook: ...
Instagram: ...
```

Khi load CSV vào BigQuery, dữ liệu chứa newline cần được xử lý đúng.

Pipeline sử dụng:

```python
allow_quoted_newlines=True
```

để BigQuery đọc đúng dữ liệu CSV có quoted newline.

---

# 18. Load strategy

Hiện tại pipeline sử dụng:

```text
WRITE_TRUNCATE
```

Điều này có nghĩa là mỗi lần chạy:

```text
CSV mới
   ↓
BigQuery
   ↓
thay thế dữ liệu cũ
```

Đây là chiến lược **full load**.

Project hiện tại sử dụng full load để đơn giản hóa pipeline và phù hợp với phạm vi project.

Trong hệ thống production, có thể phát triển thành:

```text
Incremental Load
MERGE
Partitioning
Deduplication
```

---

# 19. Main pipeline

File:

```text
main.py
```

đóng vai trò orchestrator.

Nó không chứa logic lấy dữ liệu mà chỉ điều phối:

```text
1. Extract videos
2. Extract comments
3. Transform
4. Load BigQuery
```

Có thể chạy toàn bộ pipeline bằng:

```bash
python main.py
```

Tư duy:

```text
main.py
   │
   ├── get_videos
   │
   ├── get_comments
   │
   ├── transform
   │
   └── load_bigquery
```

Điều này giúp các module vẫn có thể chạy độc lập khi debug.

---

# 20. Logging

Pipeline sử dụng Python `logging`.

Log được lưu tại:

```text
logs/pipeline.log
```

Đồng thời log cũng được hiển thị trên terminal.

Ví dụ:

```text
2026-09-17 14:30:01 - INFO - YOUTUBE DATA PIPELINE STARTED
2026-09-17 14:30:02 - INFO - [1/4] EXTRACT VIDEOS
2026-09-17 14:35:10 - INFO - [2/4] EXTRACT COMMENTS
2026-09-17 14:40:20 - INFO - [3/4] TRANSFORM DATA
2026-09-17 14:41:05 - INFO - [4/4] LOAD BIGQUERY
2026-09-17 14:41:20 - INFO - PIPELINE SUCCESS
```

Nếu pipeline xảy ra exception, logging sẽ ghi:

```text
PIPELINE FAILED
```

kèm traceback.

---

# 21. Environment variables

API key và thông tin project không hard-code trực tiếp trong source code.

File:

```text
.env
```

có dạng:

```env
YOUTUBE_API_KEY=your_api_key
GCP_PROJECT_ID=project-4930c412-dc8e-44fb-b17
BQ_DATASET=youtube_analytics
```

Trong Python:

```python
os.getenv("YOUTUBE_API_KEY")
```

được sử dụng để đọc API key.

---

# 22. Tại sao không push `.env` lên GitHub?

`.env` chứa secret:

```text
YOUTUBE_API_KEY
```

Nếu public lên GitHub, người khác có thể sử dụng API key.

Vì vậy `.gitignore` chứa:

```text
.env
```

Thay vào đó project có:

```text
.env.example
```

Ví dụ:

```env
YOUTUBE_API_KEY=
GCP_PROJECT_ID=project-4930c412-dc8e-44fb-b17
BQ_DATASET=youtube_analytics
```

`.env.example` chỉ mô tả cấu trúc config, không chứa secret thật.

---

# 23. Cài đặt project

Clone project:

```bash
git clone <repository-url>
cd youtube-data-pipeline
```

Tạo virtual environment:

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Cài dependencies:

```bash
pip install -r requirements.txt
```

---

# 24. Cấu hình environment

Copy:

```bash
cp .env.example .env
```

Sau đó điền API key:

```env
YOUTUBE_API_KEY=YOUR_API_KEY
```

---

# 25. Google Cloud authentication

Local development sử dụng Google Cloud authentication.

Sau khi cài Google Cloud CLI:

```bash
gcloud auth application-default login
```

Chọn đúng Google account.

Sau đó cấu hình project:

```bash
gcloud config set project project-4930c412-dc8e-44fb-b17
```

Cấu hình quota project:

```bash
gcloud auth application-default set-quota-project project-4930c412-dc8e-44fb-b17
```

---

# 26. Chạy từng module

Có thể chạy riêng từng bước để debug.

## Tìm channel

```bash
python etl/get_channels.py
```

## Extract videos

```bash
python etl/get_videos.py
```

## Extract comments

```bash
python etl/get_comments.py
```

## Transform

```bash
python etl/transform.py
```

## Load BigQuery

```bash
python etl/load_bigquery.py
```

---

# 27. Chạy toàn bộ pipeline

Thay vì chạy từng file:

```bash
python main.py
```

Pipeline sẽ tự động thực hiện:

```text
Extract videos
      ↓
Extract comments
      ↓
Transform
      ↓
Load BigQuery
```

---

# 28. Kết quả thực tế

Sau quá trình chạy thử:

```text
Videos:
5,641 rows

Comments:
49,748 rows
```

BigQuery:

```text
youtube_analytics
│
├── videos
│   └── 5,641 rows
│
└── comments
    └── 49,748 rows
```

---

# 29. Kiểm tra BigQuery

Có thể kiểm tra số lượng records bằng SQL:

```sql
SELECT COUNT(*)
FROM `project-4930c412-dc8e-44fb-b17.youtube_analytics.videos`;
```

Và:

```sql
SELECT COUNT(*)
FROM `project-4930c412-dc8e-44fb-b17.youtube_analytics.comments`;
```

Có thể kiểm tra dữ liệu:

```sql
SELECT *
FROM `project-4930c412-dc8e-44fb-b17.youtube_analytics.videos`
LIMIT 10;
```

---

# 30. Kiểm tra data quality

Một số kiểm tra cơ bản:

## Kiểm tra video ID null

```sql
SELECT COUNT(*)
FROM `project-4930c412-dc8e-44fb-b17.youtube_analytics.videos`
WHERE video_id IS NULL;
```

## Kiểm tra duplicate video

```sql
SELECT
    video_id,
    COUNT(*) AS total
FROM `project-4930c412-dc8e-44fb-b17.youtube_analytics.videos`
GROUP BY video_id
HAVING COUNT(*) > 1;
```

## Kiểm tra comment

```sql
SELECT
    comment_id,
    COUNT(*) AS total
FROM `project-4930c412-dc8e-44fb-b17.youtube_analytics.comments`
GROUP BY comment_id
HAVING COUNT(*) > 1;
```

---

# 31. API quota

YouTube Data API sử dụng quota.

Một số API operation có quota cost khác nhau.

Vì vậy project hạn chế các request không cần thiết bằng cách:

* Batch video IDs.
* Pagination đúng cách.
* Giới hạn comments.
* Không gọi `get_channels.py` trong mỗi pipeline run.

Đặc biệt comments có thể tạo ra rất nhiều request nếu một video có nhiều pages.

---

# 32. Error handling

Pipeline có xử lý một số tình huống:

### API trả lỗi

Kiểm tra HTTP status code.

### Comments bị tắt

Bỏ qua video và tiếp tục pipeline.

### Không có channel

Bỏ qua artist đó.

### Không có videos

Bỏ qua artist đó.

### Pipeline exception

`main.py` sử dụng logging để ghi exception và báo pipeline failed.

Mục tiêu là hạn chế trường hợp một dữ liệu lỗi nhỏ khiến không biết pipeline đang lỗi ở đâu.

---

# 33. Git security

Các file không được commit:

```text
.env
*.json
data/
logs/
.venv/
__pycache__/
```

Các file có thể commit:

```text
main.py
etl/
config/
requirements.txt
README.md
.env.example
.gitignore
```

Trước khi push:

```bash
git status
```

Kiểm tra không có:

```text
.env
credential.json
service-account.json
data/
logs/
```

---

# 34. Google Cloud VM

Sau khi project chạy ổn local, source code sẽ được deploy lên Google Cloud Compute Engine.

Kiến trúc:

```text
GitHub
   ↓
Google Cloud VM
   ↓
Python Environment
   ↓
main.py
   ↓
YouTube API
   ↓
BigQuery
```

VM đóng vai trò execution environment.

---

# 35. Tại sao cần VM?

Nếu chỉ chạy:

```bash
python main.py
```

trên máy cá nhân thì pipeline chỉ chạy khi máy đang bật.

VM cho phép project chạy trên môi trường cloud.

Sau đó có thể dùng:

```text
cron
```

để tự động chạy mà không cần mở máy cá nhân.

---

# 36. Scheduling

Pipeline được thiết kế để chạy hai lần mỗi ngày:

```text
07:00
23:00
```

Cron sẽ gọi:

```bash
python main.py
```

Ví dụ cron:

```cron
0 7 * * * cd /path/to/youtube-data-pipeline && /path/to/.venv/bin/python main.py >> logs/cron.log 2>&1

0 23 * * * cd /path/to/youtube-data-pipeline && /path/to/.venv/bin/python main.py >> logs/cron.log 2>&1
```

Sau khi cấu hình, pipeline sẽ tự động:

```text
07:00
  ↓
Extract
  ↓
Transform
  ↓
BigQuery

23:00
  ↓
Extract
  ↓
Transform
  ↓
BigQuery
```

---

# 37. Current pipeline limitation

Pipeline hiện tại sử dụng full load:

```text
WRITE_TRUNCATE
```

Do đó mỗi lần chạy sẽ thay thế dữ liệu trong BigQuery.

Ngoài ra comments hiện chỉ được lấy cho tối đa:

```text
10 videos / artist
```

Đây là lựa chọn để kiểm soát runtime và API quota trong phạm vi project.

---

# 38. Hướng phát triển

Nếu phát triển project thành production pipeline, có thể cải thiện:

### Incremental loading

Chỉ lấy dữ liệu mới hoặc dữ liệu thay đổi.

### BigQuery partitioning

Partition theo:

```text
ingestion_date
```

hoặc:

```text
published_at
```

### Deduplication

Sử dụng:

```text
video_id
comment_id
```

làm key để loại duplicate.

### Raw layer

Lưu raw API response trước transform:

```text
Raw
 ↓
Staging
 ↓
Clean
 ↓
BigQuery
```

### Orchestration

Có thể thay cron bằng:

```text
Cloud Scheduler
      ↓
Cloud Run / VM
      ↓
Pipeline
```

hoặc các workflow orchestration tools.

---

# 39. Những kiến thức Data Engineering đã thực hành

Thông qua project này có thể hiểu được workflow:

```text
Source
  ↓
API
  ↓
Extract
  ↓
Raw data
  ↓
Transform
  ↓
Data warehouse
  ↓
Scheduling
  ↓
Monitoring
```

Các kiến thức chính:

* REST API
* API pagination
* API quota
* Error handling
* ETL
* Data cleaning
* Data types
* CSV
* BigQuery
* Google Cloud
* Linux
* Environment variables
* Authentication
* Git/GitHub
* Logging
* Cron
* Cloud VM

---

# 40. Điều quan trọng cần hiểu khi trình bày project

Khi được hỏi:

> "Em đã xây dựng project này như thế nào?"

Có thể giải thích theo flow:

```text
Em lấy danh sách channel ID từ YouTube Data API.

Sau đó dùng channel ID để lấy uploads playlist
và lấy danh sách video ID.

Tiếp theo em batch các video ID để lấy thông tin
chi tiết về video như title, description, statistics,
duration và published time.

Sau đó em lấy comments cho một số video được giới hạn
để kiểm soát API quota và thời gian chạy.

Dữ liệu được lưu thành CSV làm intermediate data.

Tiếp theo em transform dữ liệu, làm sạch text và
chuẩn hóa các kiểu dữ liệu.

Cuối cùng em load dữ liệu đã transform vào BigQuery
với schema được định nghĩa rõ ràng.

Toàn bộ các bước được điều phối bằng main.py,
có logging để theo dõi quá trình chạy.

Sau khi chạy local ổn định, source code được deploy
lên Google Cloud VM và sử dụng cron để chạy tự động
hai lần mỗi ngày.
```

---

# 41. Pipeline hiện tại

```text
                 YOUTUBE
                    │
                    ▼
             YouTube Data API
                    │
                    ▼
              Python Extract
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Videos              Comments
          │                   │
          └─────────┬─────────┘
                    ▼
                 Transform
                    │
                    ▼
                BigQuery
                    │
                    ▼
             Google Cloud VM
                    │
                    ▼
                  Cron
               07:00 / 23:00
```

Project hiện tại đã hoàn thành phần **Extract → Transform → Load → Orchestration → Logging**.

Phần triển khai tiếp theo là:

```text
GitHub
   ↓
Google Cloud VM
   ↓
Environment
   ↓
Authentication
   ↓
Cron
   ↓
Automatic Pipeline
```
