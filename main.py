import logging
import os

from etl import get_videos
from etl import get_comments
from etl import transform
from etl import load_bigquery


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("YOUTUBE DATA PIPELINE STARTED")
    logger.info("=" * 60)

    try:
        logger.info("[1/4] EXTRACT VIDEOS")
        get_videos.main()

        logger.info("[2/4] EXTRACT COMMENTS")
        get_comments.main()

        logger.info("[3/4] TRANSFORM DATA")
        transform.main()

        logger.info("[4/4] LOAD BIGQUERY")
        load_bigquery.main()

        logger.info("=" * 60)
        logger.info("PIPELINE SUCCESS")
        logger.info("=" * 60)

    except Exception:
        logger.exception("PIPELINE FAILED")
        raise


if __name__ == "__main__":
    main()
