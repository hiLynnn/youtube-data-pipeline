import os
import argparse

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET", "youtube_analytics")


VIDEOS_SCHEMA = [
    bigquery.SchemaField("video_id", "STRING"),
    bigquery.SchemaField("video_title", "STRING"),
    bigquery.SchemaField("description", "STRING"),
    bigquery.SchemaField("channel_id", "STRING"),
    bigquery.SchemaField("channel_title", "STRING"),
    bigquery.SchemaField("published_at", "TIMESTAMP"),
    bigquery.SchemaField("duration", "STRING"),
    bigquery.SchemaField("tags", "STRING"),
    bigquery.SchemaField("category_id", "STRING"),
    bigquery.SchemaField("view_count", "INT64"),
    bigquery.SchemaField("like_count", "INT64"),
    bigquery.SchemaField("comment_count", "INT64"),
    bigquery.SchemaField("artist_name", "STRING"),
    bigquery.SchemaField("extracted_at", "TIMESTAMP"),
    bigquery.SchemaField("source", "STRING"),
    bigquery.SchemaField("ingestion_date", "DATE"),
]


COMMENTS_SCHEMA = [
    bigquery.SchemaField("artist_name", "STRING"),
    bigquery.SchemaField("channel_id", "STRING"),
    bigquery.SchemaField("video_id", "STRING"),
    bigquery.SchemaField("comment_id", "STRING"),
    bigquery.SchemaField("parent_id", "STRING"),
    bigquery.SchemaField("author_name", "STRING"),
    bigquery.SchemaField("comment_text", "STRING"),
    bigquery.SchemaField("published_at", "TIMESTAMP"),
    bigquery.SchemaField("updated_at", "TIMESTAMP"),
    bigquery.SchemaField("like_count", "INT64"),
    bigquery.SchemaField("reply_count", "INT64"),
    bigquery.SchemaField("extracted_at", "TIMESTAMP"),
    bigquery.SchemaField("ingestion_date", "DATE"),
]


def load_csv_to_bigquery(input_file, table_name, schema):
    client = bigquery.Client(project=PROJECT_ID)

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=schema,
        allow_quoted_newlines=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    with open(input_file, "rb") as file:
        job = client.load_table_from_file(
            file,
            table_id,
            job_config=job_config
        )

    job.result()

    table = client.get_table(table_id)

    print(
        f"Đã load {table.num_rows} rows vào {table_id}"
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Load YouTube CSV data into BigQuery"
    )

    parser.add_argument(
        "--videos",
        default="data/processed/videos_transformed.csv"
    )

    parser.add_argument(
        "--comments",
        default="data/processed/comments_transformed.csv"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    print("=" * 60)
    print("LOAD VIDEOS")
    print("=" * 60)

    load_csv_to_bigquery(
        args.videos,
        "videos",
        VIDEOS_SCHEMA
    )

    print("=" * 60)
    print("LOAD COMMENTS")
    print("=" * 60)

    load_csv_to_bigquery(
        args.comments,
        "comments",
        COMMENTS_SCHEMA
    )

    print("=" * 60)
    print("BIGQUERY LOAD SUCCESS")
    print("=" * 60)


if __name__ == "__main__":
    main()