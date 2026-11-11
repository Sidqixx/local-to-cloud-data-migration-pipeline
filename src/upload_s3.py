
import os
import logging
from pathlib import Path

import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "processed"

load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-southeast-1")


def create_s3_client():
    return boto3.client(
        "s3",
        region_name=AWS_REGION
    )


def upload_files(s3_client):
    files = list(DATA_DIR.glob("*.parquet"))

    if not files:
        raise FileNotFoundError("No Parquet files found!")

    for file_path in files:
        s3_key = f"processed/{file_path.stem}/{file_path.name}"

        logger.info(f"Uploading {file_path.name}...")

        s3_client.upload_file(
            str(file_path),
            BUCKET_NAME,
            s3_key
        )

        # Verify uploaded object
        response = s3_client.head_object(
            Bucket=BUCKET_NAME,
            Key=s3_key
        )

        logger.info(
            f"Uploaded: {s3_key} | "
            f"Size: {response['ContentLength']} bytes"
        )


def main():
    if not BUCKET_NAME:
        raise ValueError("S3_BUCKET_NAME is missing!")

    logger.info("Starting S3 migration...")

    s3_client = create_s3_client()

    try:
        upload_files(s3_client)
        logger.info("S3 MIGRATION SUCCESS!")

    except ClientError:
        logger.exception("AWS S3 operation failed!")
        raise

    finally:
        s3_client.close()


if __name__ == "__main__":
    main()
